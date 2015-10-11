__author__ = 'Chris Mayes'
__email__ = 'cmayes@cmay.es'
__version__ = '0.1.0'

from datetime import datetime
import json
import logging

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import StatementLine, Statement

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('simple')


class SimpleBankPlugin(Plugin):
    """Plugin for Simple (the bank) JSON statements.

    Note that you can specify 'bank' and 'account' in ofxstatement's configuration file (accessible
    using the `ofxstatement edit-config` command or directly at
    `~/.local/share/ofxstatement/config.ini` (on Linux, at least).  Setting these values under the
    "simple section" (i.e. "[simple]") makes it easier for your personal finance application
    to recognize which account the file's data belongs to.

    Also note that transactions for zero amounts are filtered by default.  If you wish to include
    zero-amount transactions, set 'zero_filter' to 'false' in your settings.
    """

    def get_parser(self, fin):
        parser = SimpleBankJsonParser(fin, self.settings.get('charset', 'utf-8'))
        parser.statement.bank_id = self.settings.get('bank', 'Simple')
        parser.statement.account_id = self.settings.get('account', None)
        parser.statement.filter_zeros = str2bool(self.settings.get('filter_zeros', "true"))
        return parser


def process_balances(stmt):
    """
    Based on `ofxstatement.statement.recalculate_balance`. Uses the "running_balance" field
    from the Simple transaction data for fetching the start and end balance for this statement.
    If the statement has no transactions, it is returned unmodified.

    :param stmt: The statement data to process.
    :return: The statement with modified start_balance, end_balance, start_date, and_end_date.
    """
    if not stmt.lines:
        return False
    stmt.lines.sort(key=lambda x: x.date)
    first_line = stmt.lines[0]
    stmt.start_balance = (first_line.end_balance - first_line.amount)
    stmt.end_balance = stmt.lines[-1].end_balance
    stmt.start_date = min(sl.date for sl in stmt.lines)
    stmt.end_date = max(sl.date for sl in stmt.lines)
    return True


def convert_debit(amount, book_type):
    if book_type is not None and 'debit' == book_type.lower():
        return -amount
    return amount


class SimpleBankJsonParser(StatementParser):

    def split_records(self):
        """Nothing needed for JSON format."""
        pass

    def __init__(self, fin, encoding):
        self.encoding = encoding
        self.fin = fin
        self.statement = Statement()

    def parse(self):
        """Read and parse statement
            Return Statement object

            May raise exceptions.ParseException on malformed input.
            """
        with open(self.fin, 'r', encoding=self.encoding) as fhandle:
            data = json.load(fhandle)
            for line in data['transactions']:
                stmt_line = self.parse_record(line)
                if stmt_line:
                    stmt_line.assert_valid()
                    self.statement.lines.append(stmt_line)
            process_balances(self.statement)
            return self.statement

    def parse_record(self, line):
        amount = to_float(line['amounts']['amount'])
        if self.statement.filter_zeros and is_zero(amount):
            return None

        memo = line['description']
        datetime = ts_to_datetime(line['times']['when_recorded'])
        id = line['uuid']
        ledger_amount = convert_debit(amount, line['bookkeeping_type'])
        stmt_line = StatementLine(id=id, date=datetime, memo=memo, amount=ledger_amount)
        stmt_line.end_balance = to_float(line['running_balance'])
        return stmt_line


def is_zero(fval):
    """Returns whether the given float is an approximation of zero."""
    return abs(fval - 0.0) <= 0.000001


def str2bool(v):
    """Converts a string to a boolean value.  From http://stackoverflow.com/a/715468"""
    return v.lower() in ("yes", "true", "t", "1")


def to_float(json_int):
    """Converts the given integer to a float by dividing it by 10,000 and creating a
    float from the result."""
    return float(json_int/10000)


def ts_to_datetime(epoch):
    """Converts the given epoch time in milliseconds to a datetime instance."""
    return datetime.fromtimestamp(epoch/1000)


