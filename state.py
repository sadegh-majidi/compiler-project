import re


class State:
    def __init__(self, name) -> None:
        self.name = name

    def get_next_state(self, character: str):
        raise NotImplementedError

    def __eq__(self, other):
        return self.name == other.name


REGEX = {
    'digit': r'^\d$',
    'alphabet': r'^[a-zA-Z]$',
    'keyword': r'^if|else|void|int|repeat|break|until|return$',
    'symbol': r'^;|:|\[|]|\(|\)|{|}|\+|-|\*|=|<$',
    'whitespace': r'^\n|\r|\t|\v|\f| $',
    'new_line': r'^\n$',
    'slash': r'^/$',
    'single_line_comment_starter': r'^//$',
    'multi_line_comment_starter': r'^/\*$',
    'multi_line_comment_finisher': r'^\*/$',
    'equal_sign': r'^=$'
}


class InitialState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['digit'], character):
            return STATES['number']
        if re.match(REGEX['alphabet'], character):
            return STATES['identifier']
        if re.match(REGEX['symbol'], character):
            return STATES['symbol']
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX['slash'], character):
            return STATES['comment']


class NumberState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['digit'], character):
            return STATES['number']
        if re.match(REGEX['symbol'], character):
            return STATES['symbol']
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX['slash'], character):
            return STATES['comment']


class IdentifierState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['digit'], character) or re.match(REGEX['alphabet'], character):
            return STATES['identifier']
        if re.match(REGEX['symbol'], character):
            return STATES['symbol']
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX['slash'], character):
            return STATES['comment']


class SymbolState(State):
    double_equal = False

    def get_next_state(self, character: str):
        if re.match(REGEX['digit'], character):
            return STATES['number']
        if re.match(REGEX['alphabet'], character):
            return STATES['identifier']
        if re.match(REGEX['equal_sign'], character):
            if self.double_equal:
                self.double_equal = False
                return STATES['initial']
            else:
                self.double_equal = True
                return STATES['symbol']
        if re.match(REGEX['symbol'], character):
            return STATES['initial']
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX['slash'], character):
            return STATES['comment']


class CommentState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['digit'], character):
            return STATES['number']
        if re.match(REGEX['alphabet'], character):
            return STATES['identifier']
        if re.match(REGEX['symbol'], character):
            return STATES['symbol']
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX[r'^\*$'], character):
            return STATES['multi_line_comment']
        if re.match(REGEX['slash'], character):
            return STATES['single_line_comment']


class SingleLineCommentState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['digit'], character):
            return STATES['single_line_comment']
        if re.match(REGEX['single_line_comment_starter'], character):
            return STATES['single_line_comment']
        if re.match(REGEX['symbol'], character):
            return STATES['symbol']
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX['new_line'], character):
            return STATES['initial']
        if re.match(REGEX['slash'], character):
            return STATES['single_line_comment']


class MultiLineCommentState(State):

    def get_next_state(self, character: str):
        pass


class WhitespaceState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['digit'], character):
            return STATES['number']
        if re.match(REGEX['alphabet'], character):
            return STATES['identifier']
        if re.match(REGEX['symbol'], character):
            return STATES['symbol']
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX['slash'], character):
            return STATES['comment']


STATES = {
    'initial': InitialState('initial'),
    'number': NumberState('number'),
    'identifier': IdentifierState('identifier'),
    'symbol': SymbolState('symbol'),
    'comment': CommentState('comment'),
    'single_line_comment': SingleLineCommentState('single_line_comment'),
    'multi_line_comment': MultiLineCommentState('multi_line_comment'),
    'whitespace': WhitespaceState('whitespace')
}
