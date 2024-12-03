grammar = """
    comment: "#" (WORD WS_INLINE*)+

    start: (function_definition | comment)* main_function comment*

    main_function: "function" "main" "(" ")" "{" main_function_block "}"
    function_definition: "function" identifier "(" parameters? ")" "{" block "}"

    main_function_block: (comment | assignment | conditional | loop)*
    block: (comment | assignment | conditional | loop)* statement?

    conditional: "if" "(" (relational_expression | boolean_expression) ")" "{" block "}" ("else" "{" block "}")?

    loop: "for" "(" assignment ";" (relational_expression | boolean_expression) ";" assignment ")" "{" block "}"

    function_call: identifier "(" arguments? ")"
    parameters: identifier ("," identifier)*
    arguments: (identifier | NUMBER | arithmetic_expression) ("," (identifier | NUMBER | arithmetic_expression))* 

    statement: "return" (identifier | NUMBER | arithmetic_expression | function_call)

    assignment: identifier "=" (identifier | NUMBER | arithmetic_expression | function_call)

    BOOLEAN_OPERATOR: ("&&" | "||")
    boolean_expression: ("(" relational_expression ")" | "(" boolean_expression ")") BOOLEAN_OPERATOR ("(" relational_expression ")" | "(" boolean_expression ")")
    
    RELATIONAL_OPERATOR: ("<" | "<=" | ">" | ">=" | "===" | "=/=")
    relational_expression: (identifier | NUMBER | "(" arithmetic_expression ")") RELATIONAL_OPERATOR (identifier | NUMBER | "(" arithmetic_expression ")" | function_call)
    
    ARITHMETIC_OPERATOR: ("+" | "-" | "*" | "/")
    arithmetic_expression: (identifier | NUMBER | "(" arithmetic_expression ")" | function_call) ARITHMETIC_OPERATOR (identifier | NUMBER | "(" arithmetic_expression ")" | function_call)
    
    identifier: (WORD NUMBER?)+
              | identifier ("_" identifier)*
     
    %import common.WORD
    %import common.NUMBER
    %import common.WS_INLINE
    %import common.NEWLINE
    %ignore WS_INLINE 
    %ignore NEWLINE   
"""