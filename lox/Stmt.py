from . import Expr

class Stmt(object) : pass
    
class Expression(Stmt) :
    def __init__(self, expr : Expr) :
        self.expression = expr

class Print(Stmt) :
    def __init__(self, expr : Expr) :
        self.expression = expr
