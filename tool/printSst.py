from lox import Stmt
from .printAst import printAst

def printSst(stmt : Stmt, level : int) :
    #print a Statement Syntax Tree
    
    if type(stmt) == Stmt.Block :
        print("----" * level + "Block statement:")
        for statement in stmt.statements :
            printSst(statement, level + 1)
        print("----" * level + "End of block.")
    
    if type(stmt) == Stmt.If :
        print("----" * level + "If statement: ", end = "")
        printAst(stmt.condition)
        print()
        print("----" * (level + 1) + "then : ")
        printSst(stmt.thenBranch, level + 2)
        print("----" * (level + 1) + "else : ")
        printSst(stmt.elseBranch, level + 2)
    
    elif type(stmt) == Stmt.While :
        print("----" * level + "While  statement: ", end = "")
        printAst(stmt.condition)
        print()
        print("----" * (level + 1) + "body : ")
        printSst(stmt.body, level + 2)
        print("----" * (level + 1) + "end of body.")
        
    elif type(stmt) == Stmt.Expression :
        print("----" * level + "Expression statement: ", end = "")
        printAst(stmt.expression)
        print()
    
    elif type(stmt) == Stmt.Function :
        print("----" * level + "Function declaration: ", end = "")
        print(stmt.name.lexeme, end = "")
        print("(", end = "")
        for arg in stmt.params : print(arg.lexeme, end = ",")
        print("){")
        for statement in stmt.body : printSst(statement, level + 1)
        print("}")
    
    elif type(stmt) == Stmt.Return :
        print("----" * level + "Return Statement: return", end = " ")
        printAst(stmt.value)
        print()
    
    elif type(stmt) == Stmt.Print :
        print("----" * level + "Print statement: ", end = "")
        printAst(stmt.expression)
        print()
        
    elif type(stmt) == Stmt.Var :
        print("----" * level + "Var declaration: ", end = "")
        print(stmt.name.lexeme + " : ", end = "")
        printAst(stmt.initializer)
        print()
