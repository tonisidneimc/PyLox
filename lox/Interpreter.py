import sys
import time
from .TokenType import *
from .Token import *
from .Lox_Exceptions import RunTimeError, ReturnException
from . import Expr
from . import Stmt
from .Environment import *
from .Callable import *
from .LoxFunction import *

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
            self.executeBlock(statement.statements, Environment(self._environment)); return
        
        elif isinstance(statement, Stmt.Expression) :
            #evaluates this expression
            self._evaluate(statement.expression); return
        
        elif isinstance(statement, Stmt.Function) :
            #defines a function in the current environment
            function = LoxFunction(statement)
            self._environment.define(statement.name.lexeme, function); return
        
        elif isinstance(statement, Stmt.If) :
            #execute the if then/else statement
            if self._isTruth(self._evaluate(statement.condition)) :
                self._execute(statement.thenBranch)
            elif statement.elseBranch is not None :
                self._execute(statement.elseBranch)
            return;
        
        elif isinstance(statement, Stmt.While) :
            #execute the while statement
            while self._isTruth(self._evaluate(statement.condition)) :
                self._execute(statement.body)
            return;
        
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
    
    
    def executeBlock(self, statements : list, environment : Environment) :
        #enter into a new block of code/scope
        
        previous = self._environment #the current scope
        
        try :
            #enters into a new scope
            #allows to assign, define and access variables in the inner scope
            self._environment = environment
            
            for stmt in statements :
                self._execute(stmt) #execute block's statements
        
        finally :
            #restores the current scope
            self._environment = previous
            
            
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
            return self._environment.get(expr.name)
        
        elif isinstance(expr, Expr.Assign) :
            #assign to a variable defined in the current scope
            value = self._evaluate(expr.value)
            self._environment.assign(expr.name, value)
            
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
        
        if isinstance(obj, float) :
            text = str(obj)
            #discards zeroed mantissa
            return (text[:-2] if text[-2:] == ".0" else text)       
        
        return str(obj)
