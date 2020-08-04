from . import Stmt
from . import Expr
from .Token import *
from .PyLoxExceptions import PyLoxStaticError

__all__ = ["Resolver"]

"""
    The resolver analyzes the syntax tree, 
    to determine if the program violates certain consistency requirements, 
    such as binding references to 'super', 'this' and variables to the correct scope. 
"""

class Stack :
    def __init__(self) :
        self._stack = []
    
    def push(self, data) -> None:   
        self._stack.append(data); return
    
    def pop(self) -> object:
        if self.isEmpty() : return
        return self._stack.pop();
    
    def top(self) -> object:
        return self._stack[-1]
    
    def clear(self) -> None:
        self._stack.clear(); return
    
    def __getitem__(self, index) -> object:
        if self.isEmpty() : return None
        else : return self._stack[index]
    
    def __len__(self) -> int :
        return len(self._stack)
        
    def isEmpty(self) -> bool: 
        return len(self) == 0

class StmtType :
    NONE, LOOP = range(2)

class FunctionType :
    NONE, \
    FUNCTION, \
    INITIALIZER, \
    METHOD = range(4)

class ClassType :
    CLASS,  \
    SUBCLASS, \
    NONE = range(3)
   
class Resolver :

    def __init__(self, interpreter) :
        self._hadError = False
        self._scopes = Stack()
        self._interpreter = interpreter
        self._currentScope = StmtType.NONE
        self._currentFun = FunctionType.NONE
        self._currentCls = ClassType.NONE
        
    def _beginScope(self) -> None:
        #enters into a new scope
        self._scopes.push({})
    
    def _endScope(self) -> None:
        #exit from the current scope
        #returns to a outer scope
        self._scopes.pop()
    
    def Resolve(self, what : {Stmt, Expr}) -> None:
        #Resolve all variable references
        #each statement or expression can contain one or more references of variables
        #which need to be resolved
        if isinstance(what, Stmt.Block) :
            self._beginScope()
            for stmt in what.statements :
                self.Resolve(stmt)
            self._endScope(); return
        
        elif isinstance(what, Stmt.Var) :
            self._declare(what.name)
            if what.initializer is not None :
                self.Resolve(what.initializer)
            self._define(what.name); return
        
        elif isinstance(what, Stmt.Function) :
            #name of the function is binding 
            #in the surronding scope where the function is declared
            self._declare(what.name)
            self._define(what.name)
            
            self._resolveFunction(what, FunctionType.FUNCTION); return
        
        elif isinstance(what, Stmt.Class) :
            #name of the class is binding 
            #in the surronding scope where the class is declared
            
            enclosingClass = self._currentCls #save the current state
            self._currentCls = ClassType.CLASS
            
            #allow to reference itself inside methods
            self._declare(what.name) 
            self._define(what.name)
            
            try :
                if what.supercls and what.name.lexeme == what.supercls.name.lexeme :
                    raise PyLoxStaticError(what.name, "A class cannot inherit from itself.")
            except PyLoxStaticError as error :
                error.what()     
            
            if what.supercls is not None :
                self._currentCls = ClassType.SUBCLASS #allows references to 'super'
                self.Resolve(what.supercls)
                self._beginScope() #begin a scope to define 'super'
                self._scopes.top()["super"] = True
            
            self._beginScope() #begin a scope to define 'this'
            self._scopes.top()["this"] = True
            
            for method in what.methods :
                methodName = method.name.lexeme
                self._resolveFunction(method, FunctionType.INITIALIZER if methodName == "init" 
                                         else FunctionType.METHOD)

            self._endScope(); #pop scope where 'this' is defined
            if what.supercls is not None :
                self._endScope() #pop scope where the superclass is defined
                
            self._currentCls = enclosingClass; return #restore the current state
        
        elif isinstance(what, Stmt.If) :
            #unlike Interpreter, it visit both branches
            self.Resolve(what.condition)
            self.Resolve(what.thenBranch)
            if what.elseBranch is not None :
                self.Resolve(what.elseBranch) 
            return
            
        elif isinstance(what, Stmt.Print) :
            #resolves the expression to be printed
            self.Resolve(what.expression); return
            
        elif isinstance(what, Stmt.Return) :
            try :
                if self._currentFun == FunctionType.NONE :
                    #attempt to return from top-level code
                    raise PyLoxStaticError(what.keyword, "Cannot return from top-level code.")
                if self._currentFun == FunctionType.INITIALIZER :
                    #attempt to return from an init method
                    raise PyLoxStaticError(what.keyword, "Cannot return a value from an initializer.")
                    
            except PyLoxStaticError as error :
                self._hadError = True
                error.what()
            else :
                if what.value is not None : 
                    self.Resolve(what.value)
            return
        
        elif isinstance(what, Stmt.Break) or isinstance(what, Stmt.Continue):
            try :
                if self._currentScope != StmtType.LOOP :
                    raise PyLoxStaticError(what.keyword, "Cannot use outside loops.") 
            except PyLoxStaticError as error :
                self._hadError = True
                error.what()
            else : return
        
        elif isinstance(what, Stmt.While) :
            current = self._currentScope
            self._currentScope = StmtType.LOOP
            self.Resolve(what.condition)
            self.Resolve(what.body)
            self._currentScope = current; return
        
        elif isinstance(what, Stmt.Expression) :
            self.Resolve(what.expression); return
        
        elif isinstance(what, Expr.Variable) :
            try :
                if not self._scopes.isEmpty() :
                    if what.name.lexeme in self._scopes.top() and self._scopes.top()[what.name.lexeme] is False :
                        #this variable is declared but not defined yet; 
                        #it means that the user is trying to assign a local variable to itself     
                        raise PyLoxStaticError(what.name, "Cannot read local variable in its own initializer.");
            
            except PyLoxStaticError as error:
                self._hadError = True
                error.what()
            else :
                self._resolveLocal(what, what.name); return
        
        elif isinstance(what, Expr.Chain) :
            self.Resolve(what.left)
            self.Resolve(what.right); return
        
        elif isinstance(what, Expr.Assign) :
            self.Resolve(what.value)
            self._resolveLocal(what, what.name); return
        
        elif isinstance(what, Expr.Call) :
            #Resolve the callee and their arguments
            self.Resolve(what.callee)
            for arg in what.args :
                self.Resolve(arg)
            return
        
        elif isinstance(what, Expr.This) :
            try:
                if self._currentCls == ClassType.NONE :
                    raise PyLoxStaticError(what.keyword, "Cannot use 'this' outside of a class.")
            
            except PyLoxStaticError as error:
                self._hadError = True
                error.what()
            else :
                self._resolveLocal(what, what.keyword)
        
        elif isinstance(what, Expr.Super) :
            try :
                if self._currentCls == ClassType.NONE :
                    raise PyLoxStaticError(what.keyword, "Cannot use 'super' outside of a class.")
                elif self._currentCls != ClassType.SUBCLASS :
                    raise PyLoxStaticError(what.keyword, "Cannot use 'super' in a class with no superclass.")
                        
            except PyLoxStaticError as error :
                self._hadError = True
                error.what()
            else :
                self._resolveLocal(what, what.keyword); return
        
        elif isinstance(what, Expr.Get) :
            self.Resolve(what.object); return
        
        elif isinstance(what, Expr.Set) :
            self.Resolve(what.value)
            self.Resolve(what.object); return
        
        elif isinstance(what, Expr.Literal) :
            #there is nothing to do
            #a literal expression does not mention variables and does not contain subexpressions
            return
            
        elif isinstance(what, Expr.Unary) :
           self.Resolve(what.right); return
            
        elif isinstance(what, Expr.Logical) : 
            #unlike the interpreter, does not perform short-circuit
            #visit both left and right expressions
            self.Resolve(what.left)
            self.Resolve(what.right); return
            
        elif isinstance(what, Expr.Binary) :
            self.Resolve(what.left)    
            self.Resolve(what.right); return
        
        elif isinstance(what, Expr.Ternary) :
            self.Resolve(what.condition)
            self.Resolve(what.thenValue)
            self.Resolve(what.elseValue); return
        
        elif isinstance(what, Expr.Grouping) :
            self.Resolve(what.expression); return  
            
    def _declare(self, name : Token) -> None:
        if self._scopes.isEmpty() : return
        try :
            if name.lexeme in self._scopes.top() :
                raise PyLoxStaticError(name, "Another variable with this name is already declared in this scope.")
        
        except PyLoxStaticError as error :
            self._hadError = True
            error.what()
        else :
            self._scopes.top()[name.lexeme] = False
    
    def _define(self, name : Token) -> None:
        if self._scopes.isEmpty() : return
        
        self._scopes.top()[name.lexeme] = True
    
    def _resolveLocal(self, expr : Expr, name : Token) :
        #from innermost scope to outward, looks for a matching name
        start = len(self._scopes) - 1
        stop = -1
        #iterate through the scopes in range [start, stop) by decrementing 1 for each step
        #scope_distance defines the distance between the current and the global scope
        for scope_distance in range(start, stop, -1) :
            if name.lexeme in self._scopes[scope_distance] :
                self._interpreter._resolve(expr, start - scope_distance); return
            
    def _resolveFunction(self, function : Stmt.Function, funType : FunctionType) :
        #Resolve functions and methods
        
        enclosingFun = self._currentFun
        self._currentFun = funType
        
        self._beginScope()
        for param in function.params :
            self._declare(param)
            self._define(param)
        self.Resolve(function.body)
        self._endScope()
        
        self._currentFun = enclosingFun
