from . import Expr
from . import Token

class Stmt(object) : pass

class Block(Stmt) :
    #block -> "{" statements "}"
    def __init__(self, statements : list) :
        self.statements = statements 
    
class Expression(Stmt) :
    #expression -> Unary | Binary | Grouping | Literal | Logical | Variable | Assign | Call
    def __init__(self, expr : Expr) :
        self.expression = expr

class Function(Stmt) :
    #function -> fun <name>(params) block
    def __init__(self, name : Token, params : list, body : list) :
        self.name = name
        self.params = params
        self.body = body
        
class Return(Stmt) :
    #return -> return <expression>;
    def __init__(self, keyword : Token, value : Expr) :
        self.keyword = keyword
        self.value = value

class If(Stmt) :
    #if -> if(condition) thenBranch; else elseBranch;
    def __init__(self, condition : Expr, thenBranch : Stmt, elseBranch : Stmt) :
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseBranch = elseBranch

class While(Stmt) :
    #while -> while(condition) statement;
    def __init__(self, condition : Expr, body : Stmt) :
        self.condition = condition
        self.body = body

class Print(Stmt) :
    #print -> print <expression>;
    def __init__(self, expr : Expr) :
        self.expression = expr

class Var(Stmt) :
    #var -> var <name> = initializer;
    def __init__(self, name : Token, initializer : Expr) :
        self.name = name
        self.initializer = initializer

