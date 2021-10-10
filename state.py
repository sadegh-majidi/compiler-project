class State:
    def __init__(self, name) -> None:
        self.name = name

    def get_next_state(self, character: str):
        raise NotImplementedError


REGEX = {
    'digit': r'^\d$',
    'alphabet': r'^[a-zA-Z]$',
    'keyword': r'^if|else|void|int|repeat|break|until|return$',
    'symbol': r'^;|:|\[|]|\(|\)|{|}|\+|-|\*|=|<$',
    'whitespace': r'^\n|\r|\t|\v|\f$',
    'new_line': r'^\n$',
    'slash': r'^/$',
    'single_line_comment_starter': r'^//$',
    'multi_line_comment_starter': r'^/\*$',
    'multi_line_comment_finisher': r'^\*/$'
}


class InitialState(State):

    def get_next_state(self, character: str):
        pass


class NumberState(State):

    def get_next_state(self, character: str):
        pass


class IdentifierState(State):

    def get_next_state(self, character: str):
        pass


class SymbolState(State):

    def get_next_state(self, character: str):
        pass


class SingleLineCommentState(State):

    def get_next_state(self, character: str):
        pass


class MultiLineCommentState(State):

    def get_next_state(self, character: str):
        pass


STATES = {
    'initial': InitialState('initial'),
    'number': NumberState('number'),
    'identifier': IdentifierState('identifier'),
    'symbol': SymbolState('symbol'),
    'single_line_comment': SingleLineCommentState('single_line_comment'),
    'multi_line_comment': MultiLineCommentState('multi_line_comment')
}
