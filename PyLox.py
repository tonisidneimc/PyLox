import sys
from lox.Scanner import *  
from lox.Parser import *
from lox.Resolver import *
from lox.Interpreter import *
   
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
        try :
            with open(path, "r") as reader :
                cls.buffer = reader.read()
                cls._run(cls.buffer)
        
        except FileNotFoundError :
            print("Error: Could not open file '{}': file not found.".format(path)) 
        else :
            if cls._hadError : sys.exit(65)
            if cls._hadRuntimeError : sys.exit(70)
        
    @classmethod    
    def runPrompt(cls) -> None:
        cls._interpreter.isPromptSession = True
        while True :
            print (">", end = " ")
            cls._run(input())
            cls._hadError = False
    
    @classmethod
    def _run(cls, source : str) -> None:
        scanner = Scanner(source)
        tokens = scanner.Tokenize() #step 1
        
        if cls._hasAnyError(scanner) :
            cls._hadError = True; return
        
        parser = Parser(tokens)
        statements = parser.Parse() #step 2
        
        if cls._hasAnyError(parser) :
            cls._hadError = True; return
        
        for statement in statements : 
            cls._resolver.Resolve(statement) #step 3
        
        if cls._hasAnyError(cls._resolver) :
            cls._hadError = True; return
        
        cls._interpreter.Interpret(statements) #step 4
        
        if cls._hasAnyError(cls._interpreter) :
           cls._hadRuntimeError = True; return        
         
if __name__ == "__main__" :

     if len(sys.argv) > 2 : 
        print ("Usage PyLox [script]")
        sys.exit(64)
        
     elif len(sys.argv) == 2 :
        Lox.runFile(sys.argv[1])
     
     else :
        Lox.runPrompt()
