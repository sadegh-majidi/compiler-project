# Arya Jalali 98105665
# Sadegh Majidi Yazdi 98106004

import re

from state import REGEX


class ErrorHandler:
    has_lexical_error = False
    has_syntax_error = False
    has_semantic_error = False
    has_unexpected_eof = False
    line_number = 0

    INVALID_INPUT = 'Invalid input'
    INVALID_NUMBER = 'Invalid number'
    UNCLOSED_COMMENT = 'Unclosed comment'
    UNMATCHED_COMMENT = 'Unmatched comment'

    UNEXPECTED = 'Unexpected'
    MISSING = 'missing'
    ILLEGAL = 'illegal'
    semantic_errors = []

    @staticmethod
    def write_semantic_errors_output():
        with open('semantic_errors.txt', 'w') as f:
            if ErrorHandler.semantic_errors:
                for lineno, error in ErrorHandler.semantic_errors:
                    f.write(f'#{lineno} : Semantic Error! {error}\n')
            else:
                f.write('The input program is semantically correct.\n')

    @staticmethod
    def write_syntax_error(line_number: int, error_type: str, token: str):
        with open('syntax_errors.txt', 'a') as f:
            f.write(f"#{line_number} : syntax error, {error_type} {token}\n")

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

    @classmethod
    def init_table(cls):
        cls.KEYWORDS = ['if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'endif']
        cls.global_funcs = [{
            'lexeme': "output",
            'scope': 0,
            'type': 'void',
            'role': 'function',
            'num_of_args': 1,
            'params': ['int']
        }]
        cls.symbol_table = cls.global_funcs.copy()
        cls.scope_stack = [0]
        cls.temp_stack = [0]
        cls.arg_list_stack = []
        cls.declaration_flag = False

    @classmethod
    def install_id(cls, lexeme):
        if not cls.declaration_flag:
            i = cls.find_row_index(lexeme)
            if i is not None:
                return i
        return len(cls.symbol_table)

    @classmethod
    def add_id_to_table(cls, token):
        symbol_id = cls.install_id(token[1])
        if symbol_id == len(cls.symbol_table):
            cls.insert(token[1])
        return symbol_id

    @classmethod
    def scope(cls):
        return len(cls.scope_stack) - 1

    @classmethod
    def get_enclosing_function(cls, level=1):
        try:
            return cls.symbol_table[cls.scope_stack[-level] - 1]
        except IndexError:
            return None

    @classmethod
    def insert(cls, lexeme):
        cls.symbol_table.append({"lexeme": lexeme, "scope": cls.scope()})

    @classmethod
    def find_row_index(cls, value, attr="lexeme"):
        for i in range(len(cls.symbol_table) - 1, -1, -1):
            row = cls.symbol_table[i]
            if row[attr] == value:
                return i
        return None

    @classmethod
    def find_row(cls, value, attr="lexeme"):
        for i in range(len(cls.symbol_table) - 1, -1, -1):
            row = cls.symbol_table[i]
            if row[attr] == value:
                return row
        return None

    @classmethod
    def is_token_keyword(cls, token: str):
        return bool(re.match(REGEX['keyword'], token))


class MemoryHandler:

    @classmethod
    def init_manager(cls):
        cls.pb_ptr = 0
        cls.static_base_ptr = 1000
        cls.temp_base_ptr = 5000
        cls.stack_base_ptr = 10008
        cls.ret_base_ptr = 15000

        cls.static_offset = 0
        cls.temp_offset = 0
        cls.locals_field_offset = 0
        cls.temps_field_offset = 0
        cls.arrays_field_offset = 0
        cls.args_field_offset = 4

    @classmethod
    def reset_manager(cls):
        cls.locals_field_offset = 0
        cls.arrays_field_offset = 0
        cls.temps_field_offset = 0
        cls.args_field_offset = 4

    @classmethod
    def get_static(cls, num_of_cells=1):
        static = cls.static_base_ptr + cls.static_offset
        cls.static_offset += 4 * num_of_cells
        return static

    @classmethod
    def get_temp(cls):
        temp = cls.temp_base_ptr + cls.temp_offset
        cls.temp_offset += 4
        SymbolTableHandler.temp_stack[-1] += 4
        return temp

    @classmethod
    def get_param_offset(cls):
        offset = cls.args_field_offset
        cls.args_field_offset += 4
        return offset


if __name__ == '__main__':
    from Parser import scan_and_parse

    scan_and_parse()
