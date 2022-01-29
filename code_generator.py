from compiler import SymbolTableHandler, MemoryHandler


class CodeGenerator:
    def __init__(self) -> None:
        self.PB = list()
        self.semantic_stack = list()
        self.call_stack = list()
        self.breaks_stack = list()

        self.symbol_translator = {
            '==': 'EQ',
            '<': 'LT',
            '+': 'ADD',
            '-': 'SUB'
        }

        self.actions = {
            'init': self.initial_code_gen,
            '#calc_stackframe_size': self.calculate_stack_frame_size,
            '#return_seq_callee': self.return_sequence_callee,
            '#close_stmt': self.close_statement,
            '#break_jp_save': self.break_jp_save,
            '#save': self.save,
            '#endif': self.endif_action,
            '#else': self.else_action,
            '#if_else': self.if_else_action,
            '#label': self.label,
            '#init_rep_until_stacks': self.init_repeat_until_stacks,
            '#until': self.until,
            '#set_retval': self.set_return_value,
            '#push_id': self.push_id,
            '#assign': self.assign,
            '#index_array': self.index_array,
            '#save_op': self.save_op,
            '#relop': self.add_rel_op,
            '#addop': self.add_rel_op,
            '#mult': self.mult_op,
            '#push_const': self.push_const,
            '#call_seq_caller': self.call_sequence_caller,
            '#call_seq_callee': self.call_sequence_callee,
            'finish': self.finish_code_gen
        }

    @property
    def number_of_args(self):
        return [len(x) for x in SymbolTableHandler.arg_list_stack]

    def get_static_address(self, offset):
        return MemoryHandler.static_base_ptr + offset

    def format_three_address_code(self, operator, *args):
        three_addr_code = '(' + operator.upper()
        for i in range(3):
            try:
                three_addr_code += (', ' + str(args[i]))
            except IndexError:
                three_addr_code += ', '
        three_addr_code += ')'
        return three_addr_code

    def add_intermediate_code(self, i_code, idx=None, inc=True, ins=False):
        if isinstance(i_code, tuple):
            i_code = self.format_three_address_code(i_code[0], *i_code[1:])

        if idx is None:
            idx = MemoryHandler.pb_ptr

        if ins:
            self.PB[idx] = (idx, i_code)
        else:
            self.PB.append((idx, i_code))

        if inc:
            MemoryHandler.pb_ptr += 1

    def resolve_addr(self, operand, back_patch=False):
        if isinstance(operand, int) or isinstance(operand, str):
            return operand
        elif 'address' in operand:
            return operand['address']
        else:
            t = MemoryHandler.get_temp()
            self.add_intermediate_code(
                self.format_three_address_code('ADD', MemoryHandler.static_base_ptr, f'#{operand["offset"]}', t),
                ins=back_patch
            )
            return '@' + str(t)

    def write_inter_code_output(self):
        with open('output.txt', 'w') as f:
            if self.PB:
                for line, code in self.PB:
                    f.write(f'{line}\t{code}\n')
            else:
                f.write('The output code has not been generated.')

    def initial_code_gen(self, current_token):
        self.add_intermediate_code(('ASSIGN', f'#{MemoryHandler.stack_base_ptr}', MemoryHandler.static_base_ptr))
        MemoryHandler.static_offset += 8
        for _ in range(3):
            self.add_intermediate_code(None)

    def finish_code_gen(self, current_token):
        t = MemoryHandler.get_temp()
        self.add_intermediate_code(('SUB', MemoryHandler.static_base_ptr, '#4', t), idx=1, inc=False, ins=True)
        self.add_intermediate_code(('ASSIGN', f'#{MemoryHandler.pb_ptr}', f'@{t}'), idx=2, inc=False, ins=True)
        self.add_intermediate_code(('JP', SymbolTableHandler.find_row('main')['address']), idx=3, inc=False, ins=True)

    def push_const(self, current_token):
        addr = MemoryHandler.get_static()
        const = "#" + current_token[1]
        self.add_intermediate_code(('ASSIGN', const, addr))
        self.semantic_stack.append(addr)

    def push_id(self, current_token):
        id_row = SymbolTableHandler.symbol_table[current_token[1]]
        self.semantic_stack.append(id_row)

    def assign(self, current_token):
        try:
            addr1 = self.resolve_addr(self.semantic_stack.pop())
            addr2 = self.resolve_addr(self.semantic_stack[-1])
            self.add_intermediate_code(('ASSIGN', addr1, addr2))
        except IndexError:
            pass

    def save_op(self, current_token):
        self.semantic_stack.append(self.symbol_translator[current_token[1]])

    def add_rel_op(self, current_token):
        try:
            dest = MemoryHandler.get_temp()
            addr2 = self.resolve_addr(self.semantic_stack.pop())
            operator = self.semantic_stack.pop()
            addr1 = self.resolve_addr(self.semantic_stack.pop())
            self.add_intermediate_code((operator, addr1, addr2, dest))
            self.semantic_stack.append(dest)
        except IndexError:
            pass

    def mult_op(self, current_token):
        try:
            dest = MemoryHandler.get_temp()
            addr2 = self.resolve_addr(self.semantic_stack.pop())
            addr1 = self.resolve_addr(self.semantic_stack.pop())
            self.add_intermediate_code(('MULT', addr1, addr2, dest))
            self.semantic_stack.append(dest)
        except IndexError:
            pass

    def close_statement(self, current_token):
        if self.semantic_stack:
            self.semantic_stack.pop()

    def label(self, current_token):
        self.semantic_stack.append(MemoryHandler.pb_ptr)

    def save(self, current_token):
        self.semantic_stack.append(MemoryHandler.pb_ptr)
        self.add_intermediate_code(None)

    def init_repeat_until_stacks(self, current_token):
        self.breaks_stack.append([])

    def break_jp_save(self, current_token):
        self.breaks_stack[-1].append(MemoryHandler.pb_ptr)
        self.add_intermediate_code(None)

    def until(self, current_token):
        try:
            condition = self.resolve_addr(self.semantic_stack.pop())
            jump_dest = self.semantic_stack.pop()
            self.add_intermediate_code(('JPF', condition, jump_dest))

            breaks_list = self.breaks_stack.pop()
            for bloc in breaks_list:
                self.add_intermediate_code(('JP', MemoryHandler.pb_ptr), idx=bloc, ins=True, inc=False)
        except IndexError:
            pass

    def endif_action(self, current_token):
        try:
            saved_label = self.semantic_stack.pop()
            condition = self.resolve_addr(self.semantic_stack.pop())
            self.add_intermediate_code(('JPF', condition, MemoryHandler.pb_ptr), idx=saved_label, ins=True, inc=False)
        except IndexError:
            pass

    def else_action(self, current_token):
        try:
            saved_label = self.semantic_stack.pop()
            condition = self.resolve_addr(self.semantic_stack.pop())
            self.semantic_stack.append(MemoryHandler.pb_ptr)
            self.add_intermediate_code(None)
            self.add_intermediate_code(('JPF', condition, MemoryHandler.pb_ptr), idx=saved_label, ins=True, inc=False)
        except IndexError:
            pass

    def if_else_action(self, current_token):
        try:
            saved_label = self.semantic_stack.pop()
            self.add_intermediate_code(('JP', MemoryHandler.pb_ptr), idx=saved_label, ins=True, inc=False)
        except IndexError:
            pass

    def index_array(self, current_token):
        index = self.resolve_addr(self.semantic_stack.pop())
        x = self.semantic_stack.pop()
        if 'address' in x:
            var_addr = '#' + str(x['address'])
        else:
            var_addr = self.resolve_addr(x)
        t = MemoryHandler.get_temp()
        self.add_intermediate_code(('MULT', index, '#4', t))
        self.add_intermediate_code(('ADD', str(var_addr), t, t))
        self.semantic_stack.append('@' + str(t))

    def call_sequence_caller(self, current_token, back_patch=False):
        stack = self.semantic_stack if not back_patch else self.call_stack

        if back_patch:
            callee = stack.pop()
            store_idx = MemoryHandler.pb_ptr
            t_ret_val = stack.pop()
            self.number_of_args[-1] = stack.pop()
            MemoryHandler.pb_ptr = stack.pop()
        else:
            callee = stack[-(self.number_of_args[-1] + 1)]

        caller = SymbolTableHandler.get_enclosing_function()

        if callee['lexeme'] == 'output':
            arg = stack.pop()
            stack.pop()
            arg_addr = self.resolve_addr(arg)
            self.add_intermediate_code(('ASSIGN', arg_addr, MemoryHandler.static_base_ptr + 4))
            self.add_intermediate_code(('PRINT', MemoryHandler.static_base_ptr + 4))
            self.number_of_args[-1] = 0
            self.semantic_stack.append('void')
            return

        if not back_patch:
            t_ret_val = MemoryHandler.get_temp()

        if "frame_size" in caller:
            top_sp = MemoryHandler.static_base_ptr
            frame_size = caller['frame_size']
            t_new_top_sp = MemoryHandler.get_temp()
            self.add_intermediate_code(('ADD', top_sp, '#' + str(frame_size), t_new_top_sp), ins=back_patch)
            self.add_intermediate_code(('ASSIGN', top_sp, '@' + str(t_new_top_sp)), ins=back_patch)
            t_args = MemoryHandler.get_temp()
            self.add_intermediate_code(('ADD', t_new_top_sp, "#4", t_args), ins=back_patch)
            n_args = callee["num_of_args"]
            args = stack[-n_args:]
            for i in range(n_args):
                stack.pop()
                arg = args[i]
                arg_addr = self.resolve_addr(arg, back_patch)
                if callee['params'][i] == 'array' and (not (isinstance(arg_addr, str) and arg_addr.startswith('@'))):
                    arg_addr = f"#{arg_addr}"
                self.add_intermediate_code(('ASSIGN', arg_addr, '@' + str(t_args)), ins=back_patch)
                self.add_intermediate_code(('ADD', t_args, "#4", t_args), ins=back_patch)
            fun_addr = stack.pop()['address']
            t_ret_addr = MemoryHandler.get_temp()
            t_ret_val_callee = MemoryHandler.get_temp()
            self.add_intermediate_code(('SUB', t_new_top_sp, "#4", t_ret_addr), ins=back_patch)
            self.add_intermediate_code(('SUB', t_new_top_sp, "#8", t_ret_val_callee), ins=back_patch)
            self.add_intermediate_code(('ASSIGN', t_new_top_sp, top_sp), ins=back_patch)
            self.add_intermediate_code(('ASSIGN', f'#{MemoryHandler.pb_ptr + 2}', f'@{t_ret_addr}'), ins=back_patch)
            self.add_intermediate_code(('JP', fun_addr), ins=back_patch)
            if callee['type'] != 'void':
                self.add_intermediate_code(('ASSIGN', MemoryHandler.ret_base_ptr, t_ret_val), ins=back_patch)
            else:
                self.add_intermediate_code(('JP', MemoryHandler.pb_ptr + 1), ins=back_patch)

        else:
            callee = stack[-(self.number_of_args[-1] + 1)]
            self.call_stack += self.semantic_stack[-(self.number_of_args[-1] + 1):]
            num_offset_vars = 0
            for i in range(1, callee['num_of_args'] + 1):
                arg = self.semantic_stack[-i]
                if not isinstance(arg, int) and 'offset' in arg:
                    num_offset_vars += 1
            self.semantic_stack = self.semantic_stack[:-(self.number_of_args[-1] + 1)]
            self.call_stack.append(MemoryHandler.pb_ptr)
            self.call_stack.append(self.number_of_args[-1])
            self.call_stack.append(t_ret_val)
            self.call_stack.append(callee)

            for _ in range(9 + callee['num_of_args'] * 2 + num_offset_vars):
                self.add_intermediate_code(None)

        if back_patch:
            MemoryHandler.pb_ptr = store_idx
        else:
            if callee['type'] == 'void':
                self.semantic_stack.append('void')
            else:
                self.semantic_stack.append(t_ret_val)

    def call_sequence_callee(self, current_token):
        pass

    def return_sequence_callee(self, current_token):
        t1 = MemoryHandler.get_temp()
        self.add_intermediate_code(('SUB', MemoryHandler.static_base_ptr, '#4', t1))
        t2 = MemoryHandler.get_temp()
        func = SymbolTableHandler.get_enclosing_function()
        if func['lexeme'] != 'main':
            self.add_intermediate_code(('ASSIGN', '@' + str(MemoryHandler.static_base_ptr), MemoryHandler.static_base_ptr))
        self.add_intermediate_code(('ASSIGN', '@' + str(t1), t2))
        self.add_intermediate_code(('JP', '@' + str(t2)))

    def set_return_value(self, current_token):
        t = MemoryHandler.get_temp()
        self.add_intermediate_code(('SUB', MemoryHandler.static_base_ptr, '#8', t))
        try:
            func = SymbolTableHandler.get_enclosing_function()
            if func['type'] != 'void':
                return_value_addr = self.resolve_addr(self.semantic_stack.pop())
            else:
                return_value_addr = '#0'
            self.add_intermediate_code(('ASSIGN', return_value_addr, '@' + str(t)))
            self.add_intermediate_code(('ASSIGN', '@' + str(t), MemoryHandler.ret_base_ptr))
        except IndexError:
            self.add_intermediate_code(('ASSIGN', '#0', '@' + str(t)))

    def calculate_stack_frame_size(self, current_token):
        func_row = SymbolTableHandler.get_enclosing_function()
        func_row["args_size"] = 0
        func_row["locals_size"] = 0
        func_row["arrays_size"] = 0
        func_row["temps_size"] = SymbolTableHandler.temp_stack.pop()
        if not SymbolTableHandler.temp_stack:
            SymbolTableHandler.temp_stack = [0]
        for i in range(SymbolTableHandler.scope_stack[-1], len(SymbolTableHandler.symbol_table)):
            if SymbolTableHandler.symbol_table[i]["role"] == "local_var":
                if SymbolTableHandler.symbol_table[i]["type"] == "array":
                    func_row["arrays_size"] += 4 * SymbolTableHandler.symbol_table[i]["num_of_args"]
                func_row["locals_size"] += 4
            else:
                func_row["args_size"] += 4

        func_row["frame_size"] = func_row["args_size"] + func_row["locals_size"] + func_row["arrays_size"] + func_row["temps_size"] + 12
        func_row["args_offset"] = 4
        func_row["locals_offset"] = func_row["args_offset"] + func_row["args_size"]
        func_row["arrays_offset"] = func_row["locals_offset"] + func_row["locals_size"]
        func_row["temps_offset"] = func_row["arrays_offset"] + func_row["arrays_size"]

        while self.call_stack:
            self.call_sequence_caller(current_token, True)

        MemoryHandler.reset_manager()

    def code_gen(self, action_symbol, current_token):
        try:
            self.actions[action_symbol](current_token)
        except Exception as e:
            print(f'Error in semantic routine {action_symbol}:', str(e))
