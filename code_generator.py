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

    def resolve_addr(self, operand):
        if isinstance(operand, int) or isinstance(operand, str):
            return operand
        elif 'address' in operand:
            return operand['address']
        else:
            t = MemoryHandler.get_temp()
            self.add_intermediate_code(
                self.format_three_address_code('ADD', MemoryHandler.static_base_ptr, f'#{operand["offset"]}', t)
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
        var_addr = self.resolve_addr(self.semantic_stack.pop())
        t = MemoryHandler.get_temp()
        self.add_intermediate_code(('MULT', index, '#4', t))
        self.add_intermediate_code(('ADD', '#' + str(var_addr), t, t))
        self.semantic_stack.append('@' + str(t))

    def call_sequence_caller(self, current_token):
        pass

    def call_sequence_callee(self, current_token):
        pass

    def return_sequence_callee(self, current_token):
        pass

    def set_return_value(self, current_token):
        pass

    def calculate_stack_frame_size(self, current_token):
        pass

    def code_gen(self, action_symbol, current_token):
        try:
            self.actions[action_symbol](current_token)
        except Exception as e:
            print(f"Error in semantic routine {action_symbol}:", str(e))
