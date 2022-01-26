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

        self.arg_array = False
        self.arg_array_addr = 0

        self.semantic_check_actions = {
              '@save_type': self.save_type,
              '@assign_type': self.assign_type,
              '@assign_fun_role': self.assign_function_role,
              '@assign_var_role': self.assign_var_role,
              '@assign_length': self.assign_length,
              '@inc_scope': self.increase_scope,
              '@assign_fun_attrs': self.assign_func_attrs,
              '@dec_scope': self.decrease_scope,
              '@save_param': self.save_param,
              '@assign_param_role': self.assign_param_role,
              '@check_break': self.check_breaks,
              '@push_until': self.push_repeat_until,
              '@pop_until': self.pop_repeat_until,
              '@check_decl': self.check_declaration,
              '@save_fun': self.save_function,
              '@save_type_check': self.save_type_check,
              '@type_check': self.check_type,
              '@index_array': self.index_array_push,
              '@index_array_pop': self.index_array_pop,
              '@push_arg_stack': self.push_arg_stack,
              '@check_args': self.check_args,
              '@pop_arg_stack': self.pop_arg_stack,
              '@save_arg': self.save_arg
        }

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

    def change_arg_array_type(self):
        SymbolTableHandler.arg_list_stack[-1][self.arg_array_addr] = 'int'
        self.arg_array = False

    def save_arg(self, current_token, line_number):
        if current_token[0] == "ID":
            SymbolTableHandler.arg_list_stack[-1].append(SymbolTableHandler.symbol_table[current_token[1]].get('type'))
            if SymbolTableHandler.arg_list_stack[-1][-1] == 'array':
                self.arg_array = True
                self.arg_array_addr = len(SymbolTableHandler.arg_list_stack[-1]-1)
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

    def check_declaration(self, current_token, line_number):
        if 'type' not in SymbolTableHandler.symbol_table[current_token[1]]:
            lexeme = self.get_lexeme(current_token)
            ErrorHandler.has_semantic_error = True
            ErrorHandler.semantic_errors.append((line_number, f"'{lexeme}' is not defined."))

    def save_function(self, current_token, line_number):
        if SymbolTableHandler.symbol_table[current_token[1]].get('role') == 'function':
            self.func_check_stack.append(current_token[1])

    def check_args(self, current_token, line_number):
        if self.func_check_stack:
            func_id = self.func_check_stack.pop()
            lexeme = SymbolTableHandler.symbol_table[func_id]['lexeme']
            args = SymbolTableHandler.arg_list_stack[-1]
            if args is not None:
                self.type_check_stack = self.type_check_stack[:len(args)]
                if SymbolTableHandler.symbol_table[func_id]['num_of_args'] != len(args):
                    ErrorHandler.has_semantic_error = True
                    ErrorHandler.semantic_errors.append((line_number, f"Mismatch in numbers of arguments of '{lexeme}'."))
                else:
                    params = SymbolTableHandler.symbol_table[func_id]['params']
                    i = 1
                    for param, arg in zip(params, args):
                        if param != arg and arg is not None:
                            ErrorHandler.has_semantic_error = True
                            ErrorHandler.semantic_errors.append((line_number, f"Mismatch in type of argument {i} of '{lexeme}'. Expected '{param}' but got '{arg}' instead."))
                        i += 1

    def push_repeat_until(self, current_token, line_number):
        self.rep_until_counter += 1

    def pop_repeat_until(self, current_token, line_number):
        self.rep_until_counter -= 1

    def check_breaks(self, current_token, line_number):
        if self.rep_until_counter <= 0:
            ErrorHandler.has_semantic_error = True
            ErrorHandler.semantic_errors.append((line_number, "No 'repeat ... until' found for 'break'."))

    def save_type_check(self, current_token, line_number):
        if current_token[0] == 'ID':
            _type = SymbolTableHandler.symbol_table[current_token[1]].get('type')
        else:
            _type = 'int'
        self.type_check_stack.append(_type)

    def index_array_push(self, current_token, line_number):
        if self.type_check_stack:
            self.type_check_stack[-1] = 'int'

    def index_array_pop(self, current_token, line_number):
        if self.type_check_stack:
            self.type_check_stack.pop()

    def check_type(self, current_token, line_number):
        try:
            operand2_type = self.type_check_stack.pop()
            operand1_type = self.type_check_stack.pop()
            if operand2_type is not None and operand1_type is not None:
                if operand1_type == 'array':
                    ErrorHandler.has_semantic_error = True
                    ErrorHandler.semantic_errors.append((line_number, f"Type mismatch in operands, Got {operand1_type} instead of int."))
                elif operand1_type != operand2_type:
                    ErrorHandler.has_semantic_error = True
                    ErrorHandler.semantic_errors.append((line_number, f"Type mismatch in operands, Got {operand2_type} instead of {operand1_type}."))
                else:
                    self.type_check_stack.append(operand1_type)
        except IndexError:
            pass

    def semantic_check(self, action_symbol, current_token, line_number):
        try:
            self.semantic_check_actions[action_symbol](current_token, line_number)
        except Exception as e:
            print(f'{line_number} : Error in semantic routine {action_symbol}:', str(e))
