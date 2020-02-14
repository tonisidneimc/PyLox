from . import Expr
from . import Token

class Stmt(object) : pass

class Block(Stmt) :
    def __init__(self, statements : list) :
        self.statements = statements 
    
class Expression(Stmt) :
    def __init__(self, expr : Expr) :
        self.expression = expr

class If(Stmt) :
    def __init__(self, condition : Expr, thenBranch : Stmt, elseBranch : Stmt) :
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

class Print(Stmt) :
    def __init__(self, expr : Expr) :
        self.expression = expr

class Var(Stmt) :
    def __init__(self, name : Token, initializer : Expr) :
        self.name = name
        self.initializer = initializer

