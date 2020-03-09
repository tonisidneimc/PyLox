import sys
from lox.Scanner import *  
from lox.Parser import *
from lox.Resolver import *
from lox.Interpreter import *
from tool.printSst import printSst
    
class Lox :
    _hadError = False
    _hadRuntimeError = False
    _interpreter = Interpreter()
    _resolver = Resolver(_interpreter)
    
    @classmethod
    def _hasAnyError(cls, step : object) -> bool :
        if step is not None:
            return step._hadError
        return True
        
    @classmethod
    def runFile(cls, path : str) -> None: 
        with open(path, "r") as reader :
            cls.buffer = reader.read()
            cls._run(cls.buffer)
         
        if cls._hadError : sys.exit(65)
        if cls._hadRuntimeError : sys.exit(70)
        
    @classmethod    
    def runPrompt(cls) -> None:
        while True :
            print (">", end = " ")
            cls._run(input())
            cls._hadError = False
    
    @classmethod
    def _run(cls, source : str) -> None:
        scanner = Scanner(source)
        tokens = scanner.Tokenize()
        
        if cls._hasAnyError(scanner) :
            cls._hadError = True; return
        
        #for token in tokens : print(token.tokenValue)
        
        parser = Parser(tokens)
        statements = parser.Parse()
        
        if cls._hasAnyError(parser) :
            cls._hadError = True; return
        
        #for statement in statements :
        #    printSst(statement, level = 0)
        #    print()
        
        for statement in statements : 
            cls._resolver.resolve(statement)
        
        if cls._hasAnyError(cls._resolver) :
            cls._hadError = True; return
        
        #for expr in cls._interpreter._locals.keys() :
        #    print (expr.name.lexeme, "->" ,cls._interpreter._locals[expr])
        
        cls._interpreter.Interpret(statements)
        
        if cls._hasAnyError(cls._interpreter) :
           cls._hadRuntimeError = True; return        
         
if __name__ == "__main__" :
     if len(sys.argv) > 2 : 
        print ("Usage jlox [script]")
        sys.exit(64)
        
     elif len(sys.argv) == 2 :
        Lox.runFile(sys.argv[1])
     
     else :
        Lox.runPrompt()
