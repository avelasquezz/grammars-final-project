import sys
import utils

from lark import Lark, exceptions, tree, Token
from grammar import grammar
from pathlib import Path

def load_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
    return null

def create_ast(code, parser):
    try:
        syntax_tree = parser.parse(code)
        return syntax_tree
    except exceptions.LarkError as e:
        print("Syntax error!\n\n", e)
        return False
    
def explore_subtree(ast, out):
    for c in ast.children:
        translate_program(c, out)
    
def process_main_function(ast, out):
    out.write("define dso_local i32 @main() #0 {\n")
    explore_subtree(ast, out)
    out.write("\tret i32 0\n" + "}")

def process_function_definition(ast, out):
    function_identifier_tree = ast.children[0]
    function_identifier = utils.get_identifier(function_identifier_tree)

    out.write(f"define dso_local i32 @{function_identifier}() #0 " + "{\n")
    explore_subtree(ast, out)
    out.write("}\n\n")

    parameters_tree = ast.children[1]
    utils.functions[function_identifier] = utils.get_function_parameterers(parameters_tree)

def write_arithmetic_expression(left, operator, right, out):
    match operator:
        case "+":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = add nsw i32 {left}, {right}\n")
        
        case "-":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = sub nsw i32 {left}, {right}\n")

        case "*":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = mul nsw i32 {left}, {right}\n")

        case "/":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = sdiv i32 {left}, {right}\n")

def write_relational_expression(left, operator, right, out):
    match operator:
        case "===":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = icmp eq i32 {left}, {right}\n")
        
        case "=/=":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = icmp ne i32 {left}, {right}\n")

        case "<":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = icmp slt i32 {left}, {right}\n")
            
        case "<=":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = icmp sle i32 {left}, {right}\n")

        case ">":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = icmp sgt i32 {left}, {right}\n")

        case ">=":
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = icmp sge i32 {left}, {right}\n")

def process_relational_expression_node(out, node):
    if isinstance(node, tree.Tree) and node.data == "arithmetic_expression":
        process_arithemtic_expression(node, out)

        return f"%{len(utils.variables)}"
    
    elif isinstance(node, tree.Tree) and node.data == "relational_expression":
        process_relational_expression(node, out)

        return f"%{len(utils.variables)}"
    
    elif isinstance(node, tree.Tree) and node.data == "identifier":
        variable_identifier = utils.get_identifier(node)

        if utils.variable_exists(variable_identifier):
            variable_number = utils.get_variable_number(variable_identifier)
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = load i32, ptr %{variable_number}, align 4\n")

            return f"%{len(utils.variables)}"
            
    else:
        return f"{node.value}"
    
def process_relational_expression(ast, out):
    left, operator, right = ast.children
    
    left_value = process_relational_expression_node(out, left)
    right_value = process_relational_expression_node(out, right)

    write_relational_expression(left_value, operator.value, right_value, out)

def process_arithmetic_expression_node(out, node):
    if isinstance(node, tree.Tree) and node.data == "arithmetic_expression":
        process_arithemtic_expression(node, out)

        return f"%{len(utils.variables)}"

    elif isinstance(node, tree.Tree) and node.data == "identifier":
        variable_identifier = utils.get_identifier(node)

        if utils.variable_exists(variable_identifier):
            variable_number = utils.get_variable_number(variable_identifier)
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = load i32, ptr %{variable_number}, align 4\n")

            return f"%{len(utils.variables)}"
    
    elif isinstance(node, tree.Tree) and node.data == "function_call":
        identifier_tree = node.children[0]
        function_identifier = utils.get_identifier(identifier_tree)

        if utils.functions_exists(function_identifier):
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = call i32 @{function_identifier}()\n")

            return f"%{len(utils.variables)}"
    
    else:
        return f"{node.value}"

def process_arithemtic_expression(ast, out):
    left, operator, right = ast.children
    
    left_value = process_arithmetic_expression_node(out, left)
    right_value = process_arithmetic_expression_node(out, right)

    write_arithmetic_expression(left_value, operator.value, right_value, out)

def process_assignment(ast, out):
    variable_identifier_tree = ast.children[0]
    variable_identifier = utils.get_identifier(variable_identifier_tree)

    if not utils.variable_exists(variable_identifier):
        utils.variables.append(variable_identifier)
        variable_number = len(utils.variables)
        out.write(f"\t%{variable_number} = alloca i32, align 4\n")
    
    variable_number = utils.get_variable_number(variable_identifier)

    assignment_value_tree = ast.children[1]

    if isinstance(assignment_value_tree, tree.Tree) and assignment_value_tree.data == "arithmetic_expression":
        process_arithemtic_expression(assignment_value_tree, out)
        out.write(f"\tstore i32 %{len(utils.variables)}, ptr %{variable_number}, align 4\n")

    elif isinstance(assignment_value_tree, tree.Tree) and assignment_value_tree.data == "identifier":
        variable_to_assign_identifier = utils.get_identifier(assignment_value_tree)
        variable_to_assign_number = utils.get_variable_number(variable_to_assign_identifier)
        
        if utils.variable_exists(variable_to_assign_identifier):
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = load i32, ptr %{variable_to_assign_number}, align 4\n")
            out.write(f"\t%store i32 %{len(utils.variables)}, ptr %{variable_number}, align 4\n")

    elif isinstance(assignment_value_tree, tree.Tree) and assignment_value_tree.data == "function_call":
        identifier_tree = assignment_value_tree.children[0]
        function_identifier = utils.get_identifier(identifier_tree)

        if utils.functions_exists(function_identifier):
            utils.variables.append("")
            out.write(f"\t%{len(utils.variables)} = call i32 @{function_identifier}()\n")
            out.write(f"\t%store i32 %{len(utils.variables)}, ptr %{variable_number}, align 4\n")

    elif isinstance(assignment_value_tree, Token):
        if not utils.variable_exists(variable_identifier):
            utils.variables.append(variable_identifier)
            out.write(f"\t%{len(utils.variables)} = alloca i32, align 4\n")

        out.write(f"\tstore i32 {assignment_value_tree.value}, ptr %{len(utils.variables)}, align 4\n")

def process_conditional(ast, out):
    has_else_block = True
    if len(ast.children) == 3:
        expression, true_block, false_block = ast.children
    else:
        has_else_block = False
        expression, true_block = ast.children

    process_relational_expression(expression, out)
        
    out.write(f"\tbr i1 %{len(utils.variables)},")

    utils.variables.append("")
    true_block_number = len(utils.variables)
    out.write(f" label %{true_block_number},")

    utils.variables.append("")
    end_if_number = len(utils.variables)

    if has_else_block:
        utils.variables.append("")
        false_block_number = len(utils.variables)
        out.write(f" label %{false_block_number}\n")
    else:
        out.write(f" label %{end_if_number}\n")

    out.write(f"\n  {true_block_number}:\n") 
    explore_subtree(true_block, out)
    out.write(f"\tbr label %{end_if_number}\n") 

    if has_else_block:
        out.write(f"\n  {false_block_number}:\n") 
        explore_subtree(false_block, out)
        out.write(f"\tbr label %{end_if_number}\n") 

    out.write(f"\n  {end_if_number}:\n")

def process_statement(ast, out):
    statement_type = ast.children[0]

    if isinstance(statement_type, tree.Tree) and statement_type.data == "identifier":
        variable_identifier = utils.get_identifier(statement_type)
        variable_number = utils.get_variable_number(variable_identifier)
        
        utils.variables.append("")
        out.write(f"\t%{len(utils.variables)} = load i32, ptr %{variable_number}, align 4\n") 
        out.write(f"\t%ret i32 %{len(utils.variables)}\n") 
    
    elif isinstance(statement_type, tree.Tree) and statement_type.data == "arithmetic_expression":
        process_arithemtic_expression(statement_type, out)
        out.write(f"\t%ret i32 %{len(utils.variables)}\n")

    elif isinstance(statement_type, tree.Tree) and statement_type.data == "function_call":
        function_identifier = utils.get_identifier(statement_type)

        if utils.functions_exists(function_identifier):
            out.write(f"\t%{len(utils.variables)} = call i32 @{function_identifier}()\n")
            out.write(f"\tret i32 %{len(utils.variables)}\n")
    
    else:
        out.write(f"\t%ret i32 {statement_type.value}\n")

def translate_program(ast, out):
    if isinstance(ast, tree.Tree):
        match ast.data:
            case "main_function":
                process_main_function(ast, out)
            
            case "function_definition":
                process_function_definition(ast, out)

            case "assignment":
                process_assignment(ast, out)
            
            case "conditional":
                process_conditional(ast, out)
            
            case "statement":
                process_statement(ast, out)
            
            case _:
                explore_subtree(ast, out)
    
def compile_program():
    if (len(sys.argv) != 2):
        print("Wrong number of parameters!")
    else:
        input_file = Path(sys.argv[1])
        output_file = input_file.with_suffix(".ll")

        code = load_file(input_file)
        parser = Lark(grammar)

        ast = create_ast(code, parser)

        if ast != False:
            with open(output_file, 'w') as out:
                translate_program(ast, out)

compile_program()