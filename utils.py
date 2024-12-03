from lark import tree

variables = list()

def get_identifier(identifier_tree):    
    identifier = ""

    for c in identifier_tree.children:
        if isinstance(c, tree.Tree):
            identifier += get_identifier(c) + "_"
        else:
            identifier += c.value 
    
    return identifier.rstrip("_") # If it exists, remove the last "_"

def variable_exists(variable_identifier):
    return variable_identifier in variables

def get_variable_number(variable_identifier):
    return variables.index(variable_identifier) + 1   