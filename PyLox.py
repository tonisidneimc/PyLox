import sys
from lox.Scanner import *  
from lox.Parser import *
from tool.printAst import printAst
    
class Lox :
    _hadError = False
    
    @classmethod
    def error_state(cls, step : object) -> bool :
        if step is not None:
            return step._hadError
        return True
        
    @classmethod
    def runFile(cls, path : str) -> None: 
        with open(path, "r") as reader :
            cls.buffer = reader.read()
            cls._run(cls.buffer)
         
        if cls._hadError : sys.exit(65)
    
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
        
        if cls.error_state(scanner) :
            cls._hadError = True; return
        
        #for token in tokens : print(token)
        
        parser = Parser(tokens)
        statements = parser.Parse()
        
        if cls.error_state(parser) :
            cls._hadError = True; return
        
        for statement in statements :
            printAst(statement.expression)
            print()
                
         
if __name__ == "__main__" :
     if len(sys.argv) > 2 : 
        print ("Usage jlox [script]")
        sys.exit(64)
        
     elif len(sys.argv) == 2 :
        Lox.runFile(sys.argv[1])
     
     else :
        Lox.runPrompt()
