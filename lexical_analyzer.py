from compiler import SymbolTableHandler, ErrorHandler
from errors import InvalidNumberError, UnmatchedCommentError, InvalidInputError, \
    CommentInvalidInputError
from state import STATES


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
                    self.line_number += 1

            except InvalidNumberError:
                self.token += char
                ErrorHandler.write_lexical_error(self.line_number, ErrorHandler.INVALID_NUMBER, self.token)
                self.index = index
                self.state = STATES['initial']
                self.token = ''
            except InvalidInputError:
                if self.state.name == 'symbol':
                    if self.token not in {'=', '*'}:
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
                if self.valid_tokens:
                    break
            except CommentInvalidInputError:
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
            return self.flush_tokens()
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

                if self.state == STATES['multi_line_comment'] and self.token[-2:] != '*/':
                    comment_start_line = self.line_number - self.token.count('\n')
                    ErrorHandler.write_lexical_error(comment_start_line, ErrorHandler.UNCLOSED_COMMENT, self.token[:7] + '...')

                if self.state == STATES['comment']:
                    ErrorHandler.write_lexical_error(self.line_number, ErrorHandler.INVALID_INPUT, self.token)

                self.state = STATES['initial']
                self.token = ''
                self.index = len(self.input)

                if self.valid_tokens:
                    return self.flush_tokens()

            if not ErrorHandler.has_lexical_error:
                with open('lexical_errors.txt', 'a') as f:
                    f.write('There is no lexical error.')

            return '$', '$'

    def flush_tokens(self):
        if not self.valid_tokens:
            return

        token_type_translator = {
            'number': 'NUM',
            'identifier': 'ID',
            'symbol': 'SYMBOL',
            'keyword': 'KEYWORD'
        }

        token = self.valid_tokens[0]
        token = (token_type_translator[token[0]], token[1])
        self.valid_tokens.clear()
        return token
