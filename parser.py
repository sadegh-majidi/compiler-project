import operator
import re

from anytree import Node, RenderTree

from compiler import ErrorHandler
from lexical_analyzer import LexicalAnalyzer

non_terminals_set = set()
terminals_set = set()
ll1_table = {}
firsts = dict()
follows = dict()
grammar_production_rules = []
states = []
no_error = True


class State:
    def __init__(self, Non_terminal, value, has_epsilon=False):
        self.Non_terminal = Non_terminal
        self.children = dict()
        self.has_epsilon = has_epsilon
        self.value = value


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


head_node = TreeNode('Program', parent=None)
all_nodes = [head_node]


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
        if rule[0] == current_token:
            cur_state = states[state_count]
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


def get_first_state(child):
    for i in range(len(states)):
        if states[i].Non_terminal == child:
            return states[i]


def parse():
    global all_nodes, head_node, no_error
    stack = [head_node, states[0]]
    scanner = LexicalAnalyzer()
    current_token = scanner.get_next_token()
    while True:
        cur_nt, cur_state = stack[-2], stack[-1]

        if cur_state.value == 1 and current_token[0] == '$':
            break
        if len(cur_state.children) == 0:
            stack.pop()
            stack.pop()
            continue
        if current_token[0] == 'KEYWORD' or current_token[0] == 'SYMBOL':
            a = current_token[1]
        else:
            a = current_token[0]
        for child, number in cur_state.children.items():
            if a in firsts[child]:
                if child in terminals_set:
                    cur_nt.add_child(TreeNode("({}, {})".format(current_token[0], current_token[1]), parent=cur_nt))
                    stack.pop()
                    stack.pop()
                    stack.append(cur_nt)
                    stack.append(states[number])
                    current_token = scanner.get_next_token()
                else:
                    new_child = TreeNode(child, parent=cur_nt)
                    cur_nt.add_child(new_child)
                    stack.pop()
                    stack.pop()
                    stack.append(cur_nt)
                    stack.append(states[number])
                    stack.append(new_child)
                    stack.append(get_first_state(child))
                break
            elif 'EPSILON' in firsts[child] and child not in terminals_set and a in follows[child]:
                new_child = TreeNode(child, parent=cur_nt)
                cur_nt.add_child(new_child)
                stack.pop()
                stack.pop()
                stack.append(cur_nt)
                stack.append(states[number])
                stack.append(new_child)
                stack.append(get_first_state(child))
                break

            elif child == 'EPSILON' and a in follows[cur_state.Non_terminal]:
                cur_nt.add_child(TreeNode('epsilon', parent=cur_nt))
                stack.pop()
                stack.pop()
                break

        else:
            no_error = False
            child = list(cur_state.children.items())[0]
            child_state = states[child[1]]

            if child[0] in terminals_set and child[0] != a and a != '$':
                stack.pop()
                stack.pop()
                stack.append(cur_nt)
                stack.append(child_state)
                ErrorHandler.write_syntax_error(scanner.line_number, ErrorHandler.MISSING, list(cur_state.children.keys())[0])
            elif a in follows[child[0]]:
                stack.pop()
                stack.pop()
                stack.append(cur_nt)
                stack.append(child_state)
                ErrorHandler.write_syntax_error(scanner.line_number, ErrorHandler.MISSING, child[0])
            else:
                if a == '$':
                    ErrorHandler.has_unexpected_eof = True
                    line_num = scanner.input.count('\n')
                    ErrorHandler.write_syntax_error(line_num + 1, ErrorHandler.UNEXPECTED, 'EOF')
                    break
                else:
                    ErrorHandler.write_syntax_error(scanner.line_number, ErrorHandler.ILLEGAL, a)
                    current_token = scanner.get_next_token()


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



def drawTree(root, new_root):
    for child in root.children:
        drawTree(child, Node(child.value, parent=new_root))


def scan_and_parse():
    split_grammar_rules()
    find_terminals_and_non_terminals()
    set_first_and_follows()

    initialize_diagrams()
    parse()

    calculate_depth()
    all_nodes.sort(key=operator.attrgetter('depth'))
    head_print_node = Node(head_node.value)
    drawTree(head_node, head_print_node)

    if not ErrorHandler.has_unexpected_eof:
        Node('$', parent=head_print_node)

    with open('parse_tree.txt', 'w') as f:
        x = True
        for pre, fill, node in RenderTree(head_print_node):
            if x:
                f.write('%s%s' % (pre, node.name))
                x = False
            else:
                f.write('\n%s%s' % (pre, node.name))

    if no_error:
        with open('syntax_errors.txt', 'w') as f:
            f.write('There is no syntax error.')
