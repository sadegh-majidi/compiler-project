import re

from state import REGEX


class ErrorHandler:
    has_lexical_error = False
    line_number = 0

    INVALID_INPUT = 'Invalid input'
    INVALID_NUMBER = 'Invalid number'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched comment'

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
    from lexical_analyzer import LexicalAnalyzer
    lexical_analyser = LexicalAnalyzer()
    line = 0
    while True:
        x = lexical_analyser.get_next_token()
        print(x)
        with open('tokens.txt', 'a') as f:
            if line != lexical_analyser.line_number:
                if line != 0:
                    f.write('\n')
                f.write(f'{lexical_analyser.line_number}.\t')
                line = lexical_analyser.line_number

            f.write(f'({x[0]}, {x[1]}) ')
        if x == ('$', '$'):
            break
