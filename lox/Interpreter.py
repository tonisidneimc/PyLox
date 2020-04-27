import sys
import time
from .TokenType import *
from .Token import *
from .LoxExceptions import RunTimeError, ReturnException
from . import Expr
from . import Stmt
from .Environment import *
from .Callable import *
from .LoxFunction import *
from .LoxClass import *
from .LoxInstance import *

__all__ = ["Interpreter"]

"""
    This module provides the Interpreter class, with some methods, 
    to evaluate each statement that composes the program, producing user-visible output 
    or modifying some state in the interpreter that can be detected later.
"""

class Interpreter :

    def __init__(self) :
        self._hadError = False
        self.globals = Environment() #global scope
        self._environment = self.globals
        self._locals = {}
        
        # native/built-in functions definition
        
        class Clock(Callable) :
            def arity(self) : return 0;
            def call(self, interpreter, arguments : list = []) : 
                """Using built-in python function clock. According to its documentation, 'it returns the CPU time 
                   or real time since the start of the process or since the first call to clock().  
                   This has as much precision as the system records.'
                """
                return time.clock()
            def __str__(self) :
                return "<native function clock>"
                
        self.globals.define("clock", Clock())
        
    def Interpret(self, statements : list) -> None:
        """
            interpret each Statement Syntax Tree from a parsed list of statements,
            (see Parser's documentation), evaluating and executing it.
        """
        try :
            for statement in statements :
                self._execute(statement)
            
        except RunTimeError as error :
            self._hadError = True
            error.what()
    
    def _execute(self, statement : Stmt) -> None:
        #executes a statement
        if isinstance(statement, Stmt.Block) :
            #enters into a new nested scope
            self.executeBlock(statement, Environment(self._environment)); return
        
        elif isinstance(statement, Stmt.Expression) :
            #evaluates this expression
            self._evaluate(statement.expression); return
        
        elif isinstance(statement, Stmt.Function) :
            #defines a function in the current environment
            function = LoxFunction(statement, self._environment, False)
            self._environment.define(statement.name.lexeme, function); return
        
        elif isinstance(statement, Stmt.If) :
            #execute the if then/else statement
            if self._isTruth(self._evaluate(statement.condition)) :
                self._execute(statement.thenBranch)
            elif statement.elseBranch is not None :
                self._execute(statement.elseBranch)
            return
        
        elif isinstance(statement, Stmt.While) :
            #execute the while statement
            while self._isTruth(self._evaluate(statement.condition)) :
                self._execute(statement.body)
            return
        
        elif isinstance(statement, Stmt.Return) :
            value = None if statement.value is None else self._evaluate(statement.value)
            raise ReturnException(value) #returns value
                        
        elif isinstance(statement, Stmt.Print) :
            #evaluates and print this expression
            value = self._evaluate(statement.expression)
            sys.stdout.write(self._stringify(value) + "\n"); return
        
        elif isinstance(statement, Stmt.Var) :
            #define this variable in the current environment
            value = None if statement.initializer is None else self._evaluate(statement.initializer)
            self._environment.define(statement.name.lexeme, value); return
        
        elif isinstance(statement, Stmt.Class) :
            
            if statement.supercls is not None :
                supercls = self._evaluate(statement.supercls)
                if not isinstance(supercls, LoxClass) : 
                    raise RunTimeError(statement.supercls.name, f"Superclass of '{statement.name.lexeme}' must be a class.")
            else : supercls = None
            
            self._environment.define(statement.name.lexeme, None)
            
            if supercls is not None :
                self._environment = Environment(self._environment)
                self._environment.define("super", supercls)
            
            methods = {}
            for method in statement.methods :
                methodName = method.name.lexeme
                methods[methodName] = LoxFunction(method, self._environment, True if methodName == "init" else False)
            
            klass = LoxClass(statement.name.lexeme, supercls, methods)
            if supercls is not None : 
                self._environment = self._environment.enclosing
                
            self._environment.assign(statement.name, klass)
            
    def executeBlock(self, block : Stmt.Block, environment : Environment) :
        #enter into a new block of code/scope
        
        previous = self._environment #the current scope
        try :
            #enters into a new scope
            #allows to assign, define and access variables in the inner scope
            self._environment = environment
            
            for stmt in block.statements :
                self._execute(stmt) #execute block's statements
        
        except Exception:
            raise
        finally :
            #restores the current scope
            self._environment = previous
    
    def _resolve(self, expr : Expr, depth : int) -> None:
        self._locals[expr] = depth; return             
    
    def _findVariable(self, name : Token, expr : Expr) :
        try :
            distance = self._locals[expr]
        except KeyError :
            return self.globals.get(name)
        else :
            return self._environment.getAt(distance, name.lexeme)
            
    def _evaluate(self, expr : Expr) -> object:
        #implements evaluation logic for each type of expression node in AST
        
        if isinstance(expr, Expr.Literal) :
            #returns the literal value
            return expr.value
        
        elif isinstance(expr, Expr.Logical) :
            #returns the true value of the expression
            left = self._evaluate(expr.left)
            #tries to short-circuit : if after evaluating the left operand, 
            #the result of the logical expression is known, do not evaluate the right operand
            if expr.operator.tokenValue == TokenType.OR :
                if self._isTruth(left): #true or anything else is true 
                    return left
            elif expr.operator.tokenValue == TokenType.AND :
                if not self._isTruth(left): #false and anything else is false
                    return left
            
            return self._evaluate(expr.right) #left operand only is logically inconclusive, so it evaluates the right
        
        elif isinstance(expr, Expr.Variable) :
            #returns the variable's state/value    
            return self._findVariable(expr.name, expr)
        
        elif isinstance(expr, Expr.Assign) :
            #assign to a variable defined in the current scope
            value = self._evaluate(expr.value)
            
            try : 
                #get resolved scope of this variable
                distance = self._locals[expr]
            except KeyError :
                #it is not in locals
                #assume it is in global scope
                try :
                    self.globals.assign(expr.name, value)
                except RunTimeError as error :
                    #it is not in globals
                    #tried to assign to an undefined variable
                    error.what()
            else :
                #assign to the resolved variable
                self._environment.assignAt(distance, expr.name, value)
            
            finally :
                return value #allows cascading values
        
        elif isinstance(expr, Expr.Call) : 
            callee = self._evaluate(expr.callee) #recursively evaluates callee
            
            args = [self._evaluate(arg) for arg in expr.args]
            
            if not isinstance(callee, Callable) : #check if it evaluates to a callable defined function
                raise RunTimeError(expr.paren, "Only calls to functions and classes are allowed.")
            
            function = callee
            
            if len(args) != function.arity() : 
                raise RunTimeError(expr.paren, f"Expected {function.arity()} arguments, but got {len(args)}.")
            
            return function.call(self, args) #calls the function with their specific arguments
        
        elif isinstance(expr, Expr.This) :
            return self._findVariable(expr.keyword, expr)
        
        elif isinstance(expr, Expr.Super) :
            dist = self._locals[expr]
            superclass = self._environment.getAt(dist, "super") #where superclass is defined
            #"this" is always bound right inside the environment in which "super" is stored
            thisObject = self._environment.getAt(dist - 1, "this")
            
            method = superclass.findMethod(expr.method.lexeme)
            if method is None :
                raise RunTimeError(expr.method, f"Undefined property '{expr.name.lexeme}'.")
                
            return method.bind(thisObject)
        
        elif isinstance(expr, Expr.Get) :
            obj = self._evaluate(expr.object)
            
            if isinstance(obj, LoxInstance) :
                return obj.get(expr.name)
            
            raise RunTimeError(expr.name, "Only instances have properties.")
        
        elif isinstance(expr, Expr.Set) :
            obj = self._evaluate(expr.object)
            
            if not isinstance(obj, LoxInstance) :
                raise RunTimeError(expr.name, "Only instances have fields.")
            
            value = self._evaluate(expr.value)
            obj.set(expr.name, value)
            return value
            
        elif isinstance(expr, Expr.Grouping) :
            #recursively evaluates the grouping subexpression, and returns the result
            return self._evaluate(expr.expression)
            
        elif isinstance(expr, Expr.Unary) :
            #recursively evaluates right operand and apply operation as: <operator> right
            
            right = self._evaluate(expr.right)
            
            if expr.operator.tokenValue == TokenType.MINUS :
                self._checkNumberOperands(expr.operator, right)
                return -(float(right))
            elif expr.operator.tokenValue == TokenType.BANG :
                return not(self._isTruth(right))
            
            return None #will not be reached
        
        elif isinstance(expr, Expr.Binary) :
            #recursively evaluates left and right operands and apply operation as: left <operator> right 
            
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            
            SkipOperandsVerification = [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL, TokenType.PLUS]
            
            if  expr.operator.tokenValue not in SkipOperandsVerification:
                self._checkNumberOperands(expr.operator, left, right)
            
            operations = {
                TokenType.GREATER       : (lambda : float(left) > float(right)),
                TokenType.GREATER_EQUAL : (lambda : float(left) >= float(right)),
                TokenType.LESS          : (lambda : float(left) < float(right)),
                TokenType.LESS_EQUAL    : (lambda : float(left) <= float(right)),
                TokenType.EQUAL_EQUAL   : (lambda :    (self._isEqual(left, right))),
                TokenType.BANG_EQUAL    : (lambda : not(self._isEqual(left, right))),
                TokenType.MINUS         : (lambda : float(left) - float(right)),
                TokenType.STAR          : (lambda : float(left) * float(right)),
                TokenType.SLASH         : (lambda : self._division_operation(expr.operator, left, right)),
                TokenType.PLUS          : (lambda : self._add_or_concat(expr.operator, left, right))
            }
            return operations[expr.operator.tokenValue]()
            
    
    def _checkNumberOperands(self, operator : Token, *operands : object) -> None:
        #check if all operands are of the same numeric type (float)
        
        for operand in operands :
            if not isinstance(operand, float) :
                raise RunTimeError(operator, "All operands must be numbers.")
        return
    
    def _division_operation(self, operator : Token, left : object, right : object) -> float:
        #implements the logic of the division operation, where the zeroed denominator is not allowed
        
        try :
            quocient =  float(left) / float(right)
        except ZeroDivisionError :
            raise RunTimeError(operator, "Attempted to divide by zero.")
        else :
            return quocient        
            
    def _add_or_concat(self, operator : Token, left : object, right : object) -> object:
        #implements logic for the PLUS (+) operator
        if isinstance(left, float) and isinstance(right, float) :
            #adds two numbers as <float> + <float>
            return float(left) + float(right)
        
        elif isinstance(left, str) and isinstance(right, str) :
            #concatenate left and right as <str> + <str>
            return str(left) + str(right)
        
        else :
            raise RunTimeError(operator, "Operands must be two numbers or two strings.")
    
    def _isTruth(self, obj : object) -> bool:
          #matches the Lox truth rule, where false and nil are False and everything else is True

          if obj == None : return False
          if isinstance(obj, bool) : return bool(obj)
          return True
    
    def _isEqual(self, left : object, right : object) -> bool:
        #checks equality between two objects
        
        if left == None and right == None : 
            return True
        if left == None :
            #None is only equal to None
            return False
        
        return left == right
    
    def _stringify(self, obj : object) -> str: 
        #returns a string representation (str) for the object
        
        if obj == None : return "nil"
        
        elif isinstance(obj, float) :
            text = str(obj)
            #discards zeroed mantissa
            return (text[:-2] if text[-2:] == ".0" else text)
        
        elif obj == True : return "true"
        
        elif obj == False : return "false"
        
        return str(obj)
