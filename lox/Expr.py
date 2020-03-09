from .Token import *

class Expr(object) : pass

class Grouping (Expr) :
    #grouping -> "(" expression ")"
    def __init__(self, expression : Expr) :
        self.expression = expression    
    
    def __str__(self) :
        return "(" + str(self.expression) + ")"
    
class Literal  (Expr) :
    #literal -> NUMBER | STRING | nil | true | false
    def __init__(self, value : object) : 
        self.value = value
    
    def __str__(self) :
        return str(self.value)
    
class Logical  (Expr) :
    #logical -> left <operator> right
    #operator = {and, or}
    def __init__(self, left : Expr, operator : Token, right : Expr) :
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self) :
        return str(self.left) + " " + self.operator.lexeme + " " + str(self.right)
      
class Unary (Expr) :
    #unary -> <operator> right
    #operator = {!, -}
    def __init__(self, operator : Token, right : Expr) :
        self.operator = operator
        self.right = right
    
    def __str__(self) : 
        return self.operator.lexeme + str(self.right)

class Binary   (Expr) :
    #binary -> left <operator> right
    #operator = {<, <=, >, >=, ==, !=, /, *, +, -}
    def __init__(self, left : Expr, operator : Token, right : Expr) :
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self) :
        return str(self.left) + " " + self.operator.lexeme + " " + str(self.right)

class Variable (Expr) :
    #variable -> var <name>;
    def __init__(self, name : Token) :
        self.name = name
    
    def __str__(self) :
        return self.name.lexeme

class Assign   (Expr) :
    #assign -> var <name> = value
    def __init__(self, name : Token, value : Expr) :
        self.name = name
        self.value = value
    
    def __str__(self) :
        return self.name.lexeme + " = " + str(self.value)
    
class Call  (Expr) :
    #call -> callee(args)
    def __init__(self, callee : Expr, paren : Token, args : list) :
        self.callee = callee
        self.paren = paren
        self.args = args
    
    def __str__(self) :
        args = ", ".join(str(arg) for arg in self.args)
        return str(self.callee) + "(" + args + ")"
