from compiler import SymbolTableHandler, MemoryHandler, ErrorHandler


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.type_check_stack = []
        self.type_assign_stack = []
        self.func_check_stack = []

        self.arity_counter = 0
        self.rep_until_counter = 0

        self.fun_param_list = []
        self.fun_arg_list = []

    def get_lexeme(self, token):
        if token[0] == "ID":
            return SymbolTableHandler.symbol_table[token[1]]['lexeme']
        else:
            return token[1]

    def increase_scope(self, input_token, line_number):
        SymbolTableHandler.scope_stack.append(len(SymbolTableHandler.symbol_table))

    def decrease_scope(self, input_token, line_number):
        scope_start_index = SymbolTableHandler.scope_stack.pop()
        SymbolTableHandler.symbol_table = SymbolTableHandler.symbol_table[:scope_start_index]

    def save_type(self, input_token, line_number):
        SymbolTableHandler.declaration_flag = True
        self.type_assign_stack.append(input_token[1])

    def assign_type(self, input_token, line_number):
        if input_token[0] == 'ID' and self.type_assign_stack:
            addr = input_token[1]
            SymbolTableHandler.symbol_table[addr]['type'] = self.type_assign_stack.pop()
            self.type_assign_stack.append(addr)
            SymbolTableHandler.declaration_flag = False

    def assign_function_role(self, input_token, line_number):
        if self.type_assign_stack:
            addr = self.type_assign_stack[-1]
            SymbolTableHandler.symbol_table[addr]['role'] = 'function'
            SymbolTableHandler.symbol_table[addr]['address'] = MemoryHandler.pb_ptr

    def assign_var_role(self, input_token, line_number, role='local_var'):
        if self.type_assign_stack:
            symbol_row = SymbolTableHandler.symbol_table[self.type_assign_stack[-1]]
            symbol_row['role'] = role
            if SymbolTableHandler.scope() == 0:
                symbol_row['role'] = 'global_var'
            if symbol_row['type'] == 'void':
                ErrorHandler.has_semantic_error = True
                ErrorHandler.semantic_errors.append((line_number, "Illegal type of void for '{}'.".format(symbol_row['lexeme'])))
                symbol_row.pop('type')
            if input_token[1] == '[':
                symbol_row['type'] = 'array'

    def assign_param_role(self, input_token, line_number):
        self.assign_var_role(input_token, line_number, 'param')

    def semantic_check(self, action_symbol, current_token, line_number):
        pass
