from .Token import *

class Expr(object) : pass

class Grouping (Expr) :
    #grouping -> "(" expression ")"
    def __init__(self, expression : Expr) :
        self.expression = expression    
    
class Literal  (Expr) :
    #literal -> NUMBER | STRING | nil | true | false
    def __init__(self, value : object) : 
        self.value = value

class Logical  (Expr) :
    #logical -> left <operator> right
    #operator = {and, or}
    def __init__(self, left : Expr, operator : Token, right : Expr) :
        self.left = left
        self.operator = operator
        self.right = right
      
class Unary    (Expr) :
    #unary -> <operator> right
    #operator = {!, -}
    def __init__(self, operator : Token, right : Expr) : 
        self.operator = operator
        self.right = right
	    
class Binary   (Expr) :
    #binary -> left <operator> right
    #operator = {<, <=, >, >=, ==, !=, /, *, +, -}
    def __init__(self, left : Expr, operator : Token, right : Expr) :
        self.left = left
        self.operator = operator
        self.right = right

class Variable (Expr) :
    #variable -> var <name>;
    def __init__(self, name : Token) :
        self.name = name

class Assign   (Expr) :
    #assign -> var <name> = value
    def __init__(self, name : Token, value : Expr) :
        self.name = name
        self.value = value

class Call  (Expr) :
    #call -> callee(args)
    def __init__(self, callee : Expr, paren : Token, args : list) :
        self.callee = callee
        self.paren = paren
        self.args = args
