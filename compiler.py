import re

from errors import InputProgramFinishedException, InvalidNumberError, UnmatchedCommentError, InvalidInputError
from state import STATES, REGEX


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
        for keyword in ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return']:
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


class LexicalAnalyzer:
    def __init__(self) -> None:
        self.state = STATES['initial']
        self.token = ''
        self.index = 0
        self.line_number = 1
        self.valid_tokens = []
        with open('input.txt', 'r') as f:
            self.input = f.read()
        SymbolTableHandler.init_table()

    def _get_next_token(self):
        index = self.index
        while True:
            try:
                char = self.input[index]
                index += 1
                new_state = self.state.get_next_state(char)
                if self.state.name == 'initial':
                    self.token += char
                    self.state = new_state
                elif new_state == self.state:
                    self.token += char
                elif self.state == STATES['comment'] and (new_state == STATES['single_line_comment'] or new_state == STATES['multi_line_comment']):
                    self.token += char
                    self.state = new_state
                else:
                    index -= 1

                    if self.state.name in {'number', 'identifier', 'symbol'}:
                        token_type = self.state.name
                        if token_type == 'identifier' and SymbolTableHandler.is_token_keyword(self.token):
                            token_type = 'keyword'

                        token = (token_type, self.token)
                        self.valid_tokens.append(token)
                        if token_type == 'identifier':
                            SymbolTableHandler.add_token_to_table(token)
                        self.index = index
                        self.state = STATES['initial']
                        self.token = ''
                        break

                    self.state = STATES['initial']
                    self.token = ''
                    continue

                if char == '\n':
                    self.flush_tokens()
                    self.line_number += 1
            except InvalidNumberError:
                self.token += char
                ErrorHandler.write_lexical_error(self.line_number, ErrorHandler.INVALID_NUMBER, self.token)
                self.index = index
                self.state = STATES['initial']
                self.token = ''
            except InvalidInputError:
                if self.state.name == 'symbol':
                    if self.token != '=':
                        token_type = self.state.name
                        token = (token_type, self.token)
                        self.valid_tokens.append(token)
                        self.token = ''

                if self.state.name == 'comment':
                    self.token = ''
                    char = '/'
                    index -= 1

                self.token += char
                ErrorHandler.write_lexical_error(self.line_number, ErrorHandler.INVALID_INPUT, self.token)
                self.index = index
                self.state = STATES['initial']
                self.token = ''
            except UnmatchedCommentError:
                ErrorHandler.write_lexical_error(self.line_number, ErrorHandler.UNMATCHED_COMMENT, '*/')
                self.index = index
                self.state = STATES['initial']
                self.token = ''

    def get_next_token(self):
        try:
            self._get_next_token()
        except IndexError:
            if self.token:
                if self.state.name in {'number', 'identifier', 'symbol'}:
                    token_type = self.state.name
                    if token_type == 'identifier' and SymbolTableHandler.is_token_keyword(self.token):
                        token_type = 'keyword'

                    token = (token_type, self.token)
                    self.valid_tokens.append(token)
                    if token_type == 'identifier':
                        SymbolTableHandler.add_token_to_table(token)

                self.flush_tokens()

                if self.state == STATES['multi_line_comment'] and self.token[-2:] != '*/':
                    comment_start_line = self.line_number - self.token.count('\n')
                    ErrorHandler.write_lexical_error(comment_start_line, ErrorHandler.UNCLOSED_COMMENT, self.token[:7] + '...')

                self.state = STATES['initial']
                self.token = ''

            if not ErrorHandler.has_lexical_error:
                with open('lexical_errors.txt', 'a') as f:
                    f.write('There is no lexical error.')

            raise InputProgramFinishedException()

    def flush_tokens(self):
        if not self.valid_tokens:
            return

        token_type_translator = {
            'number': 'NUM',
            'identifier': 'ID',
            'symbol': 'SYMBOL',
            'keyword': 'KEYWORD'
        }

        with open('tokens.txt', 'a') as f:
            f.write(f'{self.line_number}.\t')
            for token in self.valid_tokens:
                f.write(f'({token_type_translator[token[0]]}, {token[1]}) ')
            f.write('\n')

        self.valid_tokens.clear()


if __name__ == '__main__':
    lexical_analyser = LexicalAnalyzer()
    while True:
        try:
            lexical_analyser.get_next_token()
        except InputProgramFinishedException:
            break
