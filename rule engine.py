import re

class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        """
        :param node_type: 'operator' for AND/OR, 'operand' for conditions like 'age > 30'
        :param value: Value for operand nodes (e.g., ('age', '>', 30)) or 'AND'/'OR' for operators
        :param left: Left child node (for operators)
        :param right: Right child node (for operators)
        """
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
    """Parses a simple condition into an operand node."""
    pattern = r"(\w+)\s*(>|<|=)\s*('?\w+'?)"
    match = re.match(pattern, condition.strip())
    if match:
        return Node('operand', value=(match.group(1), match.group(2), match.group(3).strip("'")))
    else:
        raise ValueError(f"Invalid condition format: {condition}")

def parse_rule(rule_string):
    """Parses a rule string with AND/OR operators into an AST."""
    rule_string = rule_string.strip()
    if not rule_string:
        raise ValueError("Rule string cannot be empty.")
    
    # Handle AND first
    if "AND" in rule_string:
        left_rule, right_rule = rule_string.split("AND", 1)
        return Node('operator', value="AND", left=parse_rule(left_rule), right=parse_rule(right_rule))
    
    # Handle OR
    elif "OR" in rule_string:
        left_rule, right_rule = rule_string.split("OR", 1)
        return Node('operator', value="OR", left=parse_rule(left_rule), right=parse_rule(right_rule))
    
    else:
        return parse_condition(rule_string)

def combine_rules(rules):
    """Combines multiple rules into a single AST using OR operator."""
    if not rules:
        return None  # No rules to combine

    combined_ast = parse_rule(rules[0])
    for rule in rules[1:]:
        combined_ast = Node('operator', value="OR", left=combined_ast, right=parse_rule(rule))

    return combined_ast

def evaluate_rule(ast, data):
    """Evaluates the AST against the provided user data."""
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
    """Updates an existing condition in the AST."""
    if ast.type == 'operand':
        if ast.value == old_condition:
            ast.value = new_condition
    elif ast.type == 'operator':
        update_condition(ast.left, old_condition, new_condition)
        update_condition(ast.right, old_condition, new_condition)
    return ast

def add_condition(ast, condition):
    """Adds a new condition as a leaf node in the AST."""
    new_condition_node = parse_condition(condition)

    # If the current node is an operator, we can add conditions to the right
    if ast.type == 'operator':
        if ast.right is None:
            ast.right = new_condition_node
        else:
            # If there's already a right condition, add a new OR condition
            ast = Node('operator', value="OR", left=ast, right=new_condition_node)
    return ast

def remove_condition(ast, condition):
    """Removes a condition from the AST."""
    if ast.type == 'operator':
        if ast.left and ast.left.type == 'operand' and ast.left.value == condition:
            return ast.right  # Replace with right subtree
        elif ast.right and ast.right.type == 'operand' and ast.right.value == condition:
            return ast.left  # Replace with left subtree

        ast.left = remove_condition(ast.left, condition)
        ast.right = remove_condition(ast.right, condition)

    return ast

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
