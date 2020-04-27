from . import Stmt
from . import Expr
from .Token import *
from .LoxExceptions import CompileError
from enum import Enum

__all__ = ["Resolver"]

"""
    This module provides a way to properly resolve each variable's state/value in the program,
    basically, telling to the interpreter how many scopes exist between the current scope, 
    where a variable is referred to, and the scope in which it is defined.  
"""

class Stack :
    def __init__(self) :
        self._stack = []
    
    def push(self, data) -> None:   
        self._stack.append(data); return
    
    def pop(self) -> object:
        if self.isEmpty() : return
        return self._stack.pop();
    
    def clear(self) -> None:
        self._stack.clear(); return
        
    def __getitem__(self, index) -> object:
        return self._stack[index]
    
    def __len__(self) -> int :
        return len(self._stack)
    
    def isEmpty(self) -> bool: 
        try :
            foo = self[-1]
        except IndexError :
            return True
        else :
            return False

FunctionType = Enum("FunctionType", """
        NONE, 
        FUNCTION,
        INITIALIZER,
        METHOD
""")

ClassType = Enum("ClassType", """
        NONE,
        CLASS,
        SUBCLASS
""")
   
class Resolver :

    def __init__(self, interpreter) :
        self._hadError = False
        self._scopes = Stack()
        self._interpreter = interpreter
        self._currentFun = FunctionType.NONE
        self._currentCls = ClassType.NONE
        
    def _beginScope(self) -> None:
        #enters into a new scope
        self._scopes.push({})
    
    def _endScope(self) -> None:
        #exit from the current scope
        #returns to a outer scope
        self._scopes.pop()
    
    def resolve(self, what : {Stmt, Expr}) -> None:
        #resolve all variable references
        #each statement or expression can contain one or more references of variables
        #which need to be resolved
        if isinstance(what, Stmt.Block) :
            self._beginScope()
            for stmt in what.statements :
                self.resolve(stmt)
            self._endScope(); return
        
        elif isinstance(what, Stmt.Var) :
            self._declare(what.name)
            if what.initializer is not None :
                self.resolve(what.initializer)
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
            
            enclosingClass = self._currentCls
            self._currentCls = ClassType.CLASS
            
            self._declare(what.name)
            self._define(what.name)
            
            try :
                if what.supercls and what.name.lexeme == what.supercls.name.lexeme :
                    raise CompileError(what.name, "A class cannot inherit from itself.")
            except CompileError as error :
                error.what()     
            
            if what.supercls is not None :
                self._currentCls = ClassType.SUBCLASS #allows references to "super"
                self.resolve(what.supercls)
                self._beginScope() #begin a scope to define "super"
                self._scopes[-1]["super"] = True
            
            self._beginScope() #begin a scope to define "this"
            self._scopes[-1]["this"] = True
            
            for method in what.methods :
                methodName = method.name.lexeme
                self._resolveFunction(method, FunctionType.INITIALIZER if methodName == "init" 
                                         else FunctionType.METHOD)

            self._endScope(); #pop scope where "this" is defined
            if what.supercls is not None :
                self._endScope() #pop scope where the superclass is defined
                
            self._currentCls = enclosingClass; return
        
        elif isinstance(what, Stmt.If) :
            #unlike Interpreter, it visit both branches
            self.resolve(what.condition)
            self.resolve(what.thenBranch)
            if what.elseBranch is not None :
                self.resolve(what.elseBranch) 
            return
            
        elif isinstance(what, Stmt.Print) :
            self.resolve(what.expression); return
            
        elif isinstance(what, Stmt.Return) :
            try :
                if self._currentFun == FunctionType.NONE :
                    #attempt to return from top-level code
                    raise CompileError(what.keyword, "Cannot return from top-level code.")
                if self._currentFun == FunctionType.INITIALIZER :
                    #attempt to return from an init method
                    raise CompileError(what.keyword, "Cannot return a value from an initializer.")
                    
            except CompileError as error :
                self._hadError = True
                error.what()
            else :
                if what.value is not None : 
                    self.resolve(what.value)
            return
            
        elif isinstance(what, Stmt.While) :
            self.resolve(what.condition)
            self.resolve(what.body); return
        
        elif isinstance(what, Stmt.Expression) :
            self.resolve(what.expression); return
        
        elif isinstance(what, Expr.Variable) :
            try :
                if not self._scopes.isEmpty() :
                    if what.name.lexeme in self._scopes[-1] and self._scopes[-1][what.name.lexeme] is False :
                    #this variable is declared but not defined yet, 
                    #it means that the user is trying to assign a local variable to itself     
                        raise CompileError(what.name, "Cannot read local variable in its own initializer.");
            except CompileError as error:
                self._hadError = True
                error.what()
            
            else :
                self._resolveLocal(what, what.name); return
        
        elif isinstance(what, Expr.Assign) :
            self.resolve(what.value)
            self._resolveLocal(what, what.name); return
        
        elif isinstance(what, Expr.Call) :
            #resolve callee and their arguments
            self.resolve(what.callee)
            for arg in what.args :
                self.resolve(arg)
            return
        
        elif isinstance(what, Expr.This) :
            try:
                if self._currentCls == ClassType.NONE :
                    raise CompileError(what.keyword, "Cannot use 'this' outside of a class.")
            
            except CompileError as error:
                self._hadError = True
                error.what()
            else :
                self._resolveLocal(what, what.keyword)
        
        elif isinstance(what, Expr.Super) :
            try :
                if self._currentCls == ClassType.NONE :
                    raise CompileError(what.keyword, "Cannot use 'super' outside of a class.")
                elif self._currentCls != ClassType.SUBCLASS :
                    raise CompileError(what.keyword, "Cannot use 'super' in a class with no superclass.")
                        
            except CompileError as error :
                self._hadError = True
                error.what()
            else :
                self._resolveLocal(what, what.keyword); return
        
        elif isinstance(what, Expr.Get) :
            self.resolve(what.object); return
        
        elif isinstance(what, Expr.Set) :
            self.resolve(what.value)
            self.resolve(what.object); return
        
        elif isinstance(what, Expr.Literal) :
            #there is nothing to do
            #a literal expression does not mention variables and does not contain subexpressions
            return
            
        elif isinstance(what, Expr.Unary) :
           self.resolve(what.right); return
            
        elif isinstance(what, Expr.Logical) : 
            #unlike the interpreter, does not perform short-circuit
            #visit both left and right expressions
            self.resolve(what.left)
            self.resolve(what.right); return
            
        elif isinstance(what, Expr.Binary) :
            self.resolve(what.left)    
            self.resolve(what.right); return
        
        elif isinstance(what, Expr.Grouping) :
            self.resolve(what.expression); return  
            
    def _declare(self, name : Token) -> None:
        if self._scopes.isEmpty() : return
        try :
            if name.lexeme in self._scopes[-1] :
                raise CompileError(name, "Another variable with this name is already declared in this scope.")
        
        except CompileError as error :
            self._hadError = True
            error.what()
        else :
            self._scopes[-1][name.lexeme] = False
    
    def _define(self, name : Token) -> None:
        if self._scopes.isEmpty() : 
            return
        self._scopes[-1][name.lexeme] = True
    
    def _resolveLocal(self, expr : Expr, name : Token) :
        #from innermost scope to outward, looks for a matching name
        start = len(self._scopes) - 1
        stop = -1
        #iterate by scopes in range [start, stop) by decrementing 1 for each step
        #scope_distance defines the distance between the current and the global scopes
        for scope_distance in range(start, stop, -1) :
            if name.lexeme in self._scopes[scope_distance] :
                self._interpreter._resolve(expr, start - scope_distance); return
            
    def _resolveFunction(self, function : Stmt.Function, funType : FunctionType) :
        #resolve functions and methods
        
        enclosingFun = self._currentFun
        self._currentFun = funType
        
        self._beginScope()
        for param in function.params :
            self._declare(param)
            self._define(param)
        self.resolve(function.body)
        self._endScope()
        
        self._currentFun = enclosingFun
