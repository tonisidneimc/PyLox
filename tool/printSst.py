from lox import Stmt
from .printAst import printAst

def printSst(stmt : Stmt) :
    #print a Statement Syntax Tree
    
    if type(stmt) == Stmt.Expression :
        printAst(stmt.expression)
    
    elif type(stmt) == Stmt.Print :
        printAst(stmt.expression)
        
    elif type(stmt) == Stmt.Var :
        print(stmt.name.lexeme + ":", end = " ")
        printAst(stmt.initializer) 
