class parser:
    def __init__(self) -> None:
        self.current_token = ''
        with open('input.txt', 'r') as f:
            self.input = f.read()
        SymbolTableHandler.init_table()