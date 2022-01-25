from compiler import SymbolTableHandler, MemoryHandler, ErrorHandler


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.type_check_stack = []
        self.type_assign_stack = []
        self.func_check_stack = []

        self.arity_counter = 0
        self.rep_until_counter = 0

        self.func_param_list = []
        self.func_arg_list = []

    def get_lexeme(self, token):
        if token[0] == "ID":
            return SymbolTableHandler.symbol_table[token[1]]['lexeme']
        else:
            return token[1]

    def increase_scope(self, current_token, line_number):
        SymbolTableHandler.scope_stack.append(len(SymbolTableHandler.symbol_table))

    def decrease_scope(self, current_token, line_number):
        scope_start_index = SymbolTableHandler.scope_stack.pop()
        SymbolTableHandler.symbol_table = SymbolTableHandler.symbol_table[:scope_start_index]

    def save_type(self, current_token, line_number):
        SymbolTableHandler.declaration_flag = True
        self.type_assign_stack.append(current_token[1])

    def assign_type(self, current_token, line_number):
        if current_token[0] == 'ID' and self.type_assign_stack:
            addr = current_token[1]
            SymbolTableHandler.symbol_table[addr]['type'] = self.type_assign_stack.pop()
            self.type_assign_stack.append(addr)
            SymbolTableHandler.declaration_flag = False

    def assign_function_role(self, current_token, line_number):
        if self.type_assign_stack:
            addr = self.type_assign_stack[-1]
            SymbolTableHandler.symbol_table[addr]['role'] = 'function'
            SymbolTableHandler.symbol_table[addr]['address'] = MemoryHandler.pb_ptr

    def assign_var_role(self, current_token, line_number, role='local_var'):
        if self.type_assign_stack:
            symbol_row = SymbolTableHandler.symbol_table[self.type_assign_stack[-1]]
            symbol_row['role'] = role
            if SymbolTableHandler.scope() == 0:
                symbol_row['role'] = 'global_var'
            if symbol_row['type'] == 'void':
                ErrorHandler.has_semantic_error = True
                ErrorHandler.semantic_errors.append((line_number, "Illegal type of void for '{}'.".format(symbol_row['lexeme'])))
                symbol_row.pop('type')
            if current_token[1] == '[':
                symbol_row['type'] = 'array'

    def assign_param_role(self, current_token, line_number):
        self.assign_var_role(current_token, line_number, 'param')

    def assign_length(self, current_token, line_number):
        if self.type_assign_stack:
            symbol_addr = self.type_assign_stack.pop()
            symbol_row = SymbolTableHandler.symbol_table[symbol_addr]
            if current_token[0] == 'NUM':
                symbol_row['num_of_args'] = int(current_token[1])
                if symbol_row['role'] == 'param':
                    symbol_row['offset'] = MemoryHandler.get_param_offset()
                else:
                    symbol_row['address'] = MemoryHandler.get_static(int(current_token[1]))
            else:
                SymbolTableHandler.symbol_table[symbol_addr]['num_of_args'] = 1
                if symbol_row['role'] == 'param':
                    symbol_row['offset'] = MemoryHandler.get_param_offset()
                else:
                    symbol_row['address'] = MemoryHandler.get_static()

            if current_token[1] == '[' and self.func_param_list:
                self.func_param_list[-1] = 'array'

    def save_param(self, current_token, line_number):
        self.func_param_list.append(current_token[1])

    def push_arg_stack(self, current_token, line_number):
        SymbolTableHandler.arg_list_stack.append([])

    def pop_arg_stack(self, current_token, line_number):
        if len(SymbolTableHandler.arg_list_stack) > 1:
            SymbolTableHandler.arg_list_stack.pop()

    def save_arg(self, current_token, line_number):
        if current_token[0] == "ID":
            SymbolTableHandler.arg_list_stack[-1].append(SymbolTableHandler.symbol_table[current_token[1]].get('type'))
        else:
            SymbolTableHandler.arg_list_stack[-1].append('int')

    def assign_func_attrs(self, current_token, line_number):
        if self.type_assign_stack:
            symbol_addr = self.type_assign_stack.pop()
            params = self.func_param_list
            SymbolTableHandler.symbol_table[symbol_addr]['num_of_args'] = len(params)
            SymbolTableHandler.symbol_table[symbol_addr]['params'] = params
            self.func_param_list = []
            SymbolTableHandler.temp_stack.append(0)

    def semantic_check(self, action_symbol, current_token, line_number):
        pass
