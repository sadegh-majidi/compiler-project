import re

from errors import InvalidNumberError, UnmatchedCommentError, InvalidInputError


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
    'symbol': r'^;|:|\[|]|\(|\)|{|}|\+|-|\*|=|<|,$',
    'whitespace': r'^\n|\r|\t|\v|\f| $',
    'new_line': r'^\n$',
    'slash': r'^/$',
    'star': r'^\*$',
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
            state = STATES['symbol']
            if re.match(REGEX['star'], character):
                state.star_detected = True
            else:
                state.star_detected = False

            if re.match(REGEX['equal_sign'], character):
                state.double_equal = True
            else:
                state.double_equal = False

            return state
        if re.match(REGEX['whitespace'], character):
            return STATES['whitespace']
        if re.match(REGEX['slash'], character):
            return STATES['comment']

        raise InvalidInputError


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
        if re.match(REGEX['alphabet'], character):
            raise InvalidNumberError

        raise InvalidInputError


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

        raise InvalidInputError


class SymbolState(State):
    double_equal = False
    star_detected = False

    def get_next_state(self, character: str):
        if re.match(REGEX['slash'], character):
            self.double_equal = False
            if self.star_detected:
                self.star_detected = False
                raise UnmatchedCommentError
            self.star_detected = False
            return STATES['comment']
        if re.match(REGEX['digit'], character):
            self.double_equal = False
            self.star_detected = False
            return STATES['number']
        if re.match(REGEX['alphabet'], character):
            self.double_equal = False
            self.star_detected = False
            return STATES['identifier']
        if re.match(REGEX['equal_sign'], character):
            self.star_detected = False
            if self.double_equal:
                self.double_equal = False
                return STATES['symbol']
            else:
                self.double_equal = False
                return STATES['initial']
        if re.match(REGEX['symbol'], character):
            self.star_detected = False
            self.double_equal = False
            return STATES['initial']
        if re.match(REGEX['whitespace'], character):
            self.star_detected = False
            self.double_equal = False
            return STATES['whitespace']
        self.star_detected = False
        self.double_equal = False

        raise InvalidInputError


class CommentState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['star'], character):
            return STATES['multi_line_comment']
        if re.match(REGEX['slash'], character):
            return STATES['single_line_comment']

        raise InvalidInputError


class SingleLineCommentState(State):

    def get_next_state(self, character: str):
        if re.match(REGEX['new_line'], character):
            return STATES['whitespace']
        else:
            return STATES['single_line_comment']


class MultiLineCommentState(State):
    star_detected = False
    comment_ended = False

    def get_next_state(self, character: str):
        if re.match(REGEX['slash'], character) and (not self.comment_ended):
            if self.star_detected:
                self.star_detected = False
                self.comment_ended = True
                return STATES['multi_line_comment']
            else:
                self.comment_ended = False
                self.star_detected = False
                return STATES['multi_line_comment']

        if self.comment_ended:
            self.comment_ended = False
            self.star_detected = False
            return STATES['initial']

        self.comment_ended = False
        if re.match(REGEX['star'], character):
            self.star_detected = True
            return STATES['multi_line_comment']
        else:
            self.star_detected = False
            return STATES['multi_line_comment']


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

        return STATES['initial']


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
