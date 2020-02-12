from lox import Expr
from lox.TokenType import *
from lox.Token import *

def printAst(expr : Expr) :    
    #print a Arithmetic Syntax Tree
    
    if type(expr) == Expr.Literal :
        print(str(expr.value), end = "")
    
    elif type(expr) == Expr.Variable :
        print(expr.name.lexeme, end = "")
    
    elif type(expr) == Expr.Assign :
        print(expr.name.lexeme, end = " = ")
        printAst(expr.value)
        
    elif type(expr) == Expr.Binary :
        printAst(expr.left)
        print(" " + expr.operator.lexeme, end = " ")
        printAst(expr.right)
    
    elif type(expr) == Expr.Unary :
        print(" " + expr.operator.lexeme, end = " ")
        printAst(expr.right)
            
    elif type(expr) == Expr.Grouping :
        print("(", end = "")
        printAst(expr.expression)
        print(")", end = "")
        
    else : return
