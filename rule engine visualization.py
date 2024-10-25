import re
import os
from graphviz import Digraph

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type  # 'operator' or 'operand'
        self.value = value  # Condition tuple for operands or AND/OR for operators
        self.left = left  # Left child (only for operators)
        self.right = right  # Right child (only for operators)

    def __repr__(self):
        if self.type == 'operator':
            return f"({self.left} {self.value} {self.right})"
        else:
            return f"{self.value[0]} {self.value[1]} {self.value[2]}"

def parse_condition(condition):
    pattern = r"(\w+)\s*(>|<|=)\s*('?\w+'?)"
    match = re.match(pattern, condition.strip())
    if match:
        return Node('operand', value=(match.group(1), match.group(2), match.group(3).strip("'")))
    else:
        raise ValueError(f"Invalid condition format: {condition}")

def parse_rule(rule_string):
    rule_string = rule_string.strip()
    if not rule_string:
        raise ValueError("Rule string cannot be empty.")
    
    if "AND" in rule_string:
        left_rule, right_rule = rule_string.split("AND", 1)
        return Node('operator', value="AND", left=parse_rule(left_rule), right=parse_rule(right_rule))
    elif "OR" in rule_string:
        left_rule, right_rule = rule_string.split("OR", 1)
        return Node('operator', value="OR", left=parse_rule(left_rule), right=parse_rule(right_rule))
    else:
        return parse_condition(rule_string)

def combine_rules(rules):
    if not rules:
        return None  

    combined_ast = parse_rule(rules[0])
    for rule in rules[1:]:
        combined_ast = Node('operator', value="OR", left=combined_ast, right=parse_rule(rule))

    return combined_ast

def evaluate_rule(ast, data):
    if not isinstance(data, dict):
        raise ValueError("User data must be a dictionary.")

    if ast.type == 'operand':
        attribute, operator, value = ast.value
        
        if attribute not in data:
            raise ValueError(f"Attribute '{attribute}' not found in user data.")
        
        value = value.strip("'") if isinstance(value, str) and not value.isdigit() else (float(value) if '.' in value else int(value))
        
        if operator == '>':
            return data[attribute] > value
        elif operator == '<':
            return data[attribute] < value
        elif operator == '=':
            return data[attribute] == value
        else:
            raise ValueError(f"Unsupported operator: {operator}")

    elif ast.type == 'operator':
        left_result = evaluate_rule(ast.left, data)
        right_result = evaluate_rule(ast.right, data)

        if ast.value == "AND":
            return left_result and right_result
        elif ast.value == "OR":
            return left_result or right_result
        else:
            raise ValueError(f"Unsupported operator type: {ast.value}")

    return False

def update_condition(ast, old_condition, new_condition):
    if ast.type == 'operand':
        if ast.value == old_condition:
            ast.value = new_condition
    elif ast.type == 'operator':
        update_condition(ast.left, old_condition, new_condition)
        update_condition(ast.right, old_condition, new_condition)
    return ast

def add_condition(ast, condition):
    new_condition_node = parse_condition(condition)
    if ast.type == 'operator':
        if ast.right is None:
            ast.right = new_condition_node
        else:
            ast = Node('operator', value="OR", left=ast, right=new_condition_node)
    return ast

def remove_condition(ast, condition):
    if ast.type == 'operator':
        if ast.left and ast.left.type == 'operand' and ast.left.value == condition:
            return ast.right  
        elif ast.right and ast.right.type == 'operand' and ast.right.value == condition:
            return ast.left  

        ast.left = remove_condition(ast.left, condition)
        ast.right = remove_condition(ast.right, condition)

    return ast

def visualize_ast(ast):
    dot = Digraph()

    def add_nodes_edges(node):
        if node.type == 'operator':
            dot.node(str(id(node)), node.value)
            if node.left:
                dot.edge(str(id(node)), str(id(node.left)))
                add_nodes_edges(node.left)
            if node.right:
                dot.edge(str(id(node)), str(id(node.right)))
                add_nodes_edges(node.right)
        else:
            dot.node(str(id(node)), f"{node.value[0]} {node.value[1]} {node.value[2]}")

    add_nodes_edges(ast)
    return dot

# Sample rules
rules = [
    "age > 30 AND department = 'Sales'",
    "age < 25 AND department = 'Marketing'",
    "salary > 50000 OR experience > 5"
]

# Combine the rules into a single AST
combined_ast = combine_rules(rules)

# Print the initial combined AST
print("Initial Combined AST:", combined_ast)

# Update an existing condition
combined_ast = update_condition(combined_ast, ('age', '>', 30), ('age', '<', 40))
print("AST after updating condition:", combined_ast)

# Add a new condition
combined_ast = add_condition(combined_ast, "salary < 70000")
print("AST after adding a new condition:", combined_ast)

# Remove a condition
combined_ast = remove_condition(combined_ast, ('age', '<', 25))
print("AST after removing a condition:", combined_ast)

# Visualize the AST
ast_graph = visualize_ast(combined_ast)
print("Current Working Directory:", os.getcwd())
ast_graph.render('ast_visualization', format='png', cleanup=True)  # Saves as 'ast_visualization.png'

print("AST visualization saved as 'ast_visualization.png'.")
