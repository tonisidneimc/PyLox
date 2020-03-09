from lox import Stmt

def printSst(stmt : Stmt, level : int) :
    #print a Statement Syntax Tree
    
    if type(stmt) == Stmt.Block :
        print("----" * level + "Begin block:")
        for statement in stmt.statements :
            printSst(statement, level + 1)
        print("----" * level + "End of block.")
    
    if type(stmt) == Stmt.If :
        print("----" * level + "If statement:")
        print("----" * (level + 1) + "condition:", end = " ")
        print(stmt.condition)
        print("----" * (level + 1) + "then :")
        printSst(stmt.thenBranch, level + 2)
        if(stmt.elseBranch is not None) :
            print("----" * (level + 1) + "else :")
            printSst(stmt.elseBranch, level + 2)
    
    elif type(stmt) == Stmt.While :
        print("----" * level + "While Statement:")
        print("----" * (level + 1) + "condition:", end = " ")
        print(stmt.condition)
        printSst(stmt.body, level + 2)
        
    elif type(stmt) == Stmt.Expression :
        print("----" * level + "Expression: ", end = "")
        print(stmt.expression)
    
    elif type(stmt) == Stmt.Function :
        print("----" * level + "Function declaration: ", end = "")
        print(stmt.name.lexeme, end = "")
        print("(", end = "")
        params = ", ".join(arg.lexeme for arg in stmt.params)
        print(params, end = "")
        print(")")
        printSst(stmt.body, level + 1)
    
    elif type(stmt) == Stmt.Return :
        print("----" * level + "Return Statement:", end = " ")
        print(stmt.value)
    
    elif type(stmt) == Stmt.Print :
        print("----" * level + "Print Statement: print", end = " ")
        print(stmt.expression)
        
    elif type(stmt) == Stmt.Var :
        print("----" * level + "Var declaration:", end = " ")
        print(stmt.name.lexeme + " <- ", end = "")
        print(stmt.initializer)
