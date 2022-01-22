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

    @property
    def number_of_args(self):
        return [len(x) for x in SymbolTableHandler.arg_list_stack]

    def get_static_address(self, offset):
        return MemoryHandler.static_base_ptr + offset

    def format_three_address_code(self, operator, *args):
        three_addr_code = "(" + operator.upper()
        for i in range(3):
            try:
                three_addr_code += (", " + str(args[i]))
            except IndexError:
                three_addr_code += ", "
        three_addr_code += ")"
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
        if isinstance(operand, int):
            return operand
        elif "address" in operand:
            return operand["address"]
        else:
            t = MemoryHandler.get_temp()
            self.add_intermediate_code(
                self.format_three_address_code('ADD', MemoryHandler.static_base_ptr, f"#{operand['offset']}", t)
            )
            return "@" + str(t)

    def write_inter_code_output(self):
        with open('output.txt', 'w') as f:
            if self.PB:
                for line, code in self.PB:
                    f.write(f"{line}\t{code}\n")
            else:
                f.write("The output code has not been generated.")

    def initial_code_gen(self, current_token):
        self.add_intermediate_code(("ASSIGN", f"#{MemoryHandler.stack_base_ptr}", MemoryHandler.static_base_ptr))
        MemoryHandler.static_offset += 8
        for _ in range(3):
            self.add_intermediate_code(None)

    def finish_code_gen(self, current_token):
        t = MemoryHandler.get_temp()
        self.add_intermediate_code(('SUB', MemoryHandler.static_base_ptr, "#4", t), idx=1, inc=False, ins=True)
        self.add_intermediate_code(("ASSIGN", f"#{MemoryHandler.pb_ptr}", f"@{t}"), idx=2, inc=False, ins=True)
        self.add_intermediate_code(("JP", SymbolTableHandler.find_row("main")["address"]), idx=3, inc=False, ins=True)

    def code_gen(self, action_symbol, current_token):
        pass
