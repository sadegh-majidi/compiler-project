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

    def get_next_token(self):
        pass


if __name__ == '__main__':
    pass
