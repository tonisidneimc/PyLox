from .Token import *

class Expr(object) : pass

class Grouping (Expr) :
    def __init__(self, expression : Expr) :
        self.expression = expression    
    
class Literal  (Expr) :
    def __init__(self, value : object) : 
        self.value = value

class Logical  (Expr) :
    def __init__(self, left : Expr, operator : Token, right : Expr) :
        self.left = left
        self.operator = operator
        self.right = right
        
class Unary    (Expr) :
    def __init__(self, operator : Token, right : Expr) : 
        self.operator = operator
        self.right = right
	    
class Binary   (Expr) :
    def __init__(self, left : Expr, operator : Token, right : Expr) :
        self.left = left
        self.operator = operator
        self.right = right

class Variable (Expr) :
    def __init__(self, name : Token) :
        self.name = name

class Assign   (Expr) :
    def __init__(self, name : Token, value : Expr) :
        self.name = name
        self.value = value
