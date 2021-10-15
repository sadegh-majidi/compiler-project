from state import STATES


class ErrorHandler:
    pass


class SymbolTableHandler:
    pass


class LexicalAnalyzer:
    def __init__(self) -> None:
        self.state = STATES['initial']
        self.token = ''
        self.index = 0
        self.line_number = 1
        self.valid_tokens = []
        with open('input.txt', 'r') as f:
            self.input = f.read()

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
            else:
                index -= 1

                if self.state.name in {'number', 'identifier', 'symbol'}:
                    self.valid_tokens.append((self.state.name, self.token))
                    self.index = index
                    self.state = STATES['initial']
                    self.token = ''
                    break

                self.state = STATES['initial']
                self.token = ''
                continue

            if char == '\n':
                self.line_number += 1


if __name__ == '__main__':
    lexical_analyser = LexicalAnalyzer()
    while True:
        lexical_analyser.get_next_token()
        # try:
        #     lexical_analyser.get_next_token()
        # except:
        #     break
