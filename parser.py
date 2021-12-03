import re
import operator

# errors = open('syntax_errors.txt', 'w')
# parse_tree = open('parse_tree.txt', 'w')
import compiler

non_terminals_set = set()
terminals_set = set()
ll1_table = {}
grammar_production_rules = []
states = []
no_error = True


class State:
    def __init__(self, Non_terminal, value, has_epsilon=False):
        self.Non_terminal = Non_terminal
        self.children = dict()
        self.has_epsilon = has_epsilon
        self.value = value

    def get_next_state(self, token):
        # todo
        pass


class TreeNode:
    def __init__(self, value, width=0, parent=None):
        self.parent = parent
        self.value = value
        self.children = []
        self.width = width
        self.depth = 0
        self.height = 0
        self.is_terminal = False
        self.token = None

    def add_child(self, child):
        self.children.append(child)
        child.width = self.width + 1

    def is_leave(self):
        return len(self.children) == 0

    def __str__(self):
        return str(self.value) + " " + str(self.width) + " " + str(self.depth)

    def set_token(self, token):
        self.token = token
        self.is_terminal = True

    def show(self):
        if self.is_terminal:
            return "(" + self.token[0] + ", " + self.token[1] + ") "
        if self.value == 'ε':
            return 'epsilon'
        return self.value


def split_grammar_rules():
    global grammar_production_rules
    grammar = open('grammar_rules', 'r').read()
    grammar_production_rules = re.split('\n', grammar)
    for i in range(0, len(grammar_production_rules)):
        grammar_production_rules[i] = re.split(' -> | ', grammar_production_rules[i])


def find_terminals_and_non_terminals():
    global non_terminals_set, terminals_set
    for rule in grammar_production_rules:
        non_terminals_set.add(rule[0])
    for rule in grammar_production_rules:
        for T_or_NT in rule:
            if T_or_NT not in non_terminals_set:
                terminals_set.add(T_or_NT)


def convert_file_to_dict(file):
    all_terms = open(file, 'r').read()
    all_terms = re.split('\n', all_terms)
    for i in range(0, len(all_terms)):
        all_terms[i] = re.split(' ', all_terms[i])
    output_dict = {}
    for term in all_terms:
        key = term[0]
        output_dict[key] = set()
        for node in term[1:]:
            output_dict[key].add(node)
    return output_dict


def set_first_and_follows():
    global firsts, follows
    firsts = convert_file_to_dict("Firsts")
    for terminal in terminals_set:
        firsts[terminal] = {terminal}
    follows = convert_file_to_dict("Follows")


def initialize_diagrams():
    global states
    cur_state = State('Program', 0)
    cur_state.children['Declaration-list'] = 1
    current_token = 'Program'
    state_count = 1
    state_count_temp = 1
    states = [cur_state, State('Program', 1)]
    for rule in grammar_production_rules[1:]:
        # print(rule)
        if rule[0] == current_token:
            cur_state = states[state_count]
            # print(cur_state.Non_terminal, rule[0])
        else:
            state_count = state_count_temp = state_count_temp + 1
            cur_state = State(rule[0], state_count)
            states.append(cur_state)
            current_token = rule[0]
        for smt in rule[1:]:
            if smt == 'EPSILON':
                cur_state.has_epsilon = True
            if smt == '':
                continue

            state_count_temp += 1
            cur_state.children[smt] = state_count_temp

            cur_state = State(rule[0], state_count_temp)
            states.append(cur_state)
    for state in states:
        print(state.children, state.Non_terminal, state.value)


def create_table():
    global ll1_table

    for non_terminal in non_terminals_set:
        ll1_table[non_terminal] = {}

    # handle firsts
    rule_number = -1
    for rule in grammar_production_rules:
        rule_number += 1
        non_terminal = rule[0]
        for product in rule[1:]:
            for terminal in firsts[product]:
                if terminal != 'ε':
                    ll1_table[non_terminal][terminal] = rule_number
            if not 'ε' in firsts[product]:
                break

    # handle follows
    rule_number = -1
    for rule in grammar_production_rules:
        rule_number += 1
        non_terminal = rule[0]
        if not 'ε' in firsts[non_terminal]:
            continue
        for terminal in follows[non_terminal]:
            ll1_table[non_terminal][terminal] = rule_number

    # handle synch
    for non_terminal in non_terminals_set:
        for terminal in follows[non_terminal]:
            if terminal not in ll1_table[non_terminal]:
                ll1_table[non_terminal][terminal] = 'synch'


# def handle_error(text):
#     global no_error, errors
#     no_error = False
#     errors.write(f'#{get_line_number()} : syntax error, {text}\n')
#
#
def parse():
    global all_nodes, head_node
    stack = [head_node, states[0]]
    scanner = compiler.LexicalAnalyzer()
    current_token = scanner.get_next_token()
    while True:
        cur_nt, cur_state = stack[-2], stack[-1]
        for child, number in cur_state.items():
            if current_token[0] in child.firsts():
                stack.append(child, number)



# def ll1():
#     global all_nodes, head_node
#     stack = [head_node]
#     current_token = get_next_token()
#     is_EOF_error = False
#     while True:
#         X_node = stack[len(stack) - 1]
#         X = X_node.value
#
#         if current_token[0] == 'SYMBOL':
#             a = current_token[1]
#         elif current_token[0] == 'ID':
#             a = current_token[0]
#         elif current_token[0] == 'KEYWORD':
#             a = current_token[1]
#         elif current_token[0] == 'NUM':
#             a = current_token[0]
#         elif current_token == '$':
#             a = current_token
#
#         if X == 'ε':
#             stack.pop()
#         elif X == a and a == '$':
#             break
#         elif X == a and X in terminals_set:
#             stack.pop()
#             X_node.set_token(current_token)
#             current_token = get_next_token()
#         elif X != a and X in terminals_set:
#             handle_error('missing ' + X)
#             node = stack.pop()
#             all_nodes.remove(node)
#             try:
#                 node.parent.children.remove(node)
#             except:
#                 pass
#         elif a not in ll1_table[X]:
#             if a == '$':
#                 handle_error('unexpected EOF')
#                 is_EOF_error = True
#                 break
#             handle_error('illegal ' + a)
#             current_token = get_next_token()
#         elif ll1_table[X][a] == 'synch':
#             handle_error('missing ' + X)
#             node = stack.pop()
#             all_nodes.remove(node)
#             try:
#                 node.parent.children.remove(node)
#             except:
#                 pass
#         else:
#             rule = grammar_production_rules[ll1_table[X][a]]
#             node = stack.pop()
#             for index in range(len(rule) - 1, 0, -1):
#                 new_node = TreeNode(rule[index], parent=node)
#                 all_nodes.append(new_node)
#                 stack.append(new_node)
#                 node.add_child(new_node)
#
#     for node in stack:
#         if node.value == '$' and not is_EOF_error:
#             continue
#         all_nodes.remove(node)
#         try:
#             node.parent.children.remove(node)
#         except:
#             pass


def calculate_depth():
    global head_node

    def visit(node):
        if node.is_leave():
            return
        depth = node.depth + 1
        node.height = 0
        for index in range(len(node.children) - 1, -1, -1):
            child = node.children[index]
            child.depth = depth
            visit(child)
            depth += child.height + 1
            node.height += child.height + 1

    visit(head_node)


horizontal_lines = [0]

# def draw_tree():
#     global horizontal_lines
#     for node in all_nodes:
#         for child in node.children:
#             horizontal_lines.append(child.width)
#         for counter in range(0, node.width - 1):
#             if counter + 1 in horizontal_lines:
#                 parse_tree.write('│   ')
#             else:
#                 parse_tree.write('    ')
#         if node.width != 0:
#             if node == node.parent.children[0]:
#                 parse_tree.write('└── ')
#             else:
#                 parse_tree.write('├── ')
#         horizontal_lines.remove(node.width)
#         parse_tree.write(f'{node.show()}\n')


if __name__ == '__main__':
    split_grammar_rules()
    find_terminals_and_non_terminals()
    set_first_and_follows()
    # create_table()

    head_node = TreeNode('Program')
    all_nodes = [head_node]
    initialize_diagrams()
    parse()

    calculate_depth()
    all_nodes.sort(key=operator.attrgetter('depth'))

    # # draw_tree()
    # if no_error:
    #     errors.write('There is no syntax error.')
