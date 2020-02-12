from . import Expr
from . import Token

class Stmt(object) : pass
    
class Expression(Stmt) :
    def __init__(self, expr : Expr) :
        self.expression = expr

class Print(Stmt) :
    def __init__(self, expr : Expr) :
        self.expression = expr

class Var(Stmt) :
    def __init__(self, name : Token, initializer : Expr) :
        self.name = name
        self.initializer = initializer
