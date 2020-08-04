## PyLox Grammar
~~~
         program -> declaration* EOF
     declaration -> classDeclaration | funDeclaration | varDeclaration | statement
classDeclaration -> "class" class
           class -> IDENTIFIER ("<" IDENTIFIER)? "{" function* "}"
  funDeclaration -> "fun" function
        function -> IDENTIFIER "(" parameters? ")" block
      parameters -> IDENTIFIER ("," IDENTIFIER)*
  varDeclaration -> "var" IDENTIFIER ("=" expression)? ";"
       statement -> exprStmt | ifStmt | forStmt | printStmt | whileStmt | returnStmt | block
        exprStmt -> expression ";"
          ifStmt -> "if" "(" expression ")" statement ("else" statement)?
         forStmt -> "for" "("(varDeclaration | exprStmt | ";") expression? ";" expression? ")" statement
       printStmt -> "print" expression ";"
       whileStmt -> "while" "(" expression ")" statement
      returnStmt -> "return" expression? ";"
       breakStmt -> "break" ";"
    continueStmt -> "continue" ";"
           block -> "{" declaration* "}"
      expression -> assignment ("," assignment)*
      assignment -> ternary | (call ".")? IDENTIFIER "=" assignment
         ternary -> logic_or ("?" expression ":" expression)?
        logic_or -> logic_and ("or" logic_and)*
       logic_and -> equality ("and" equality)*
        equality -> comparison ("==" comparison | "!=" comparision)*
      comparison -> addition ("<" addition | "<=" addition | ">" addition | ">=" addition)*
        addition -> multiplication ("+" multiplication | "-" multiplication)*
  multiplication -> unary ("*" unary | "/" unary | "%" unary)*
           unary -> ("!" unary | "-" unary)* | call
            call -> primary ( "(" arguments? ")" | "." IDENTIFIER)*
       arguments -> assignment ("," assignment)*
         primary -> NUMBER | STRING | "false" | "true" | "nil" | IDENTIFIER | grouping | "super" "." IDENTIFIER   
        grouping -> "(" expression ")"
~~~
