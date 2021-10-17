import re

from state import STATES, REGEX


class ErrorHandler:
    pass


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

    def get_next_token(self):
        index = self.index
        while True:
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
        except IndexError:
            if lexical_analyser.token:
                if lexical_analyser.state.name in {'number', 'identifier', 'symbol'}:
                    token_type = lexical_analyser.state.name
                    if token_type == 'identifier' and SymbolTableHandler.is_token_keyword(lexical_analyser.token):
                        token_type = 'keyword'

                    token = (token_type, lexical_analyser.token)
                    lexical_analyser.valid_tokens.append(token)
                    if token_type == 'identifier':
                        SymbolTableHandler.add_token_to_table(token)
                lexical_analyser.flush_tokens()
                lexical_analyser.state = STATES['initial']
                lexical_analyser.token = ''
            break
