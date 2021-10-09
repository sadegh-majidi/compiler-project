# def get_next_token():
#     pass

class ErrorHandler:
    pass


class SymbolTableHandler:
    pass


class State:
    def __init__(self, name) -> None:
        self.name = name

    def get_next_state(self, character: str):
        raise NotImplementedError


class LexicalAnalyzer:
    def __init__(self) -> None:
        self.state = State('init')
        self.token = ''
        self.index = 0
        self.line_number = 1


if __name__ == '__main__':
    pass
