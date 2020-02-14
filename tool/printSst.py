from lox import Stmt
from .printAst import printAst

def printSst(stmt : Stmt, level : int) :
    #print a Statement Syntax Tree
    
    if type(stmt) == Stmt.Block :
        print("----" * level + "Block statement:")
        for statement in stmt.statements :
            print("----" * (level + 1), end = "")
            printSst(statement, level + 1)
            print()
    
    elif type(stmt) == Stmt.Expression :
        print("----" * level + "Expression statement: ", end = "")
        printAst(stmt.expression)
    
    elif type(stmt) == Stmt.Print :
        print("----" * level + "Print statement: ", end = "")
        printAst(stmt.expression)
        
    elif type(stmt) == Stmt.Var :
        print("----" * level + "Var declaration: ", end = "")
        print(stmt.name.lexeme + " : ", end = "")
        printAst(stmt.initializer)
