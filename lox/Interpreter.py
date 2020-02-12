import sys
from .TokenType import *
from .Token import *
from .Lox_Exceptions import RunTimeError
from . import Expr
from . import Stmt
from .Environment import *

__all__ = ["Interpreter"]

"""
    This module provides the Interpreter class, with some methods, 
    to evaluate each statement that composes the program, producing user-visible output 
    or modifying some state in the interpreter that can be detected later.
"""

class Interpreter :

    def __init__(self) :
        self._environment = Environment()
        self._hadError = False
    
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
        if isinstance(statement, Stmt.Expression) :
            self._evaluate(statement.expression); return
                        
        elif isinstance(statement, Stmt.Print) :
            value = self._evaluate(statement.expression)
            sys.stdout.write(self._stringify(value) + "\n"); return
        
        elif isinstance(statement, Stmt.Var) :
            value = None if statement.initializer is None else self._evaluate(statement.initializer)
            
            self._environment.define(statement.name.lexeme, value); 
            
    def _evaluate(self, expr : Expr) -> object:
        #implements evaluation logic for each type of expression node in AST
        
        if isinstance(expr, Expr.Literal) :
            return expr.value
        
        elif isinstance(expr, Expr.Variable) :
            return self._environment.get(expr.name)
        
        elif isinstance(expr, Expr.Assign) :
            value = self._evaluate(expr.value)
            self._environment.assign(expr.name, value)
            
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
            
            return None
        
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
