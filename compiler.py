# Arya Jalali 98105665
# Sadegh Majidi Yazdi 98106004

import re

from state import REGEX


class ErrorHandler:
    has_lexical_error = False
    has_syntax_error = False
    has_unexpected_eof = False
    line_number = 0

    INVALID_INPUT = 'Invalid input'
    INVALID_NUMBER = 'Invalid number'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched comment'

    UNEXPECTED = 'Unexpected'
    MISSING = 'missing'
    ILLEGAL = 'illegal'



    @staticmethod
    def write_syntax_error(line_number: int, error_type: str, token: str):
        with open('syntax_errors.txt', 'a') as f:
            f.write(f"#{line_number} : syntax error, {error_type} {token}\n")

    @staticmethod
    def write_lexical_error(line_number: int, error_type: str, error_message: str):
        ErrorHandler.has_lexical_error = True
        if line_number != ErrorHandler.line_number:
            if ErrorHandler.line_number != 0:
                with open('lexical_errors.txt', 'a') as f:
                    f.write(f'\n')
            ErrorHandler.line_number = line_number
            with open('lexical_errors.txt', 'a') as f:
                f.write(f'{line_number}.\t({error_message}, {error_type})')
        else:
            with open('lexical_errors.txt', 'a') as f:
                f.write(f' ({error_message}, {error_type})')


class SymbolTableHandler:
    table = dict()

    @staticmethod
    def init_table():
        for keyword in ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'endif']:
            with open('symbol_table.txt', 'a') as f:
                SymbolTableHandler.table[keyword] = {'type': 'keyword'}
                f.write(f'{len(SymbolTableHandler.table)}.\t{keyword}\n')

    @staticmethod
    def add_token_to_table(token: tuple):
        if token[1] not in SymbolTableHandler.table:
            with open('symbol_table.txt', 'a') as f:
                SymbolTableHandler.table[token[1]] = {'type': token[0]}
                f.write(f'{len(SymbolTableHandler.table)}.\t{token[1]}\n')

    @staticmethod
    def is_token_keyword(token: str):
        return bool(re.match(REGEX['keyword'], token))


if __name__ == '__main__':
    from Parser import scan_and_parse

    scan_and_parse()
