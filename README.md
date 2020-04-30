## PyLox
An for-study-purposes implementation of the interpreter in Python, to the __Lox__ scripting language, 
based on the *__[Crafting Interpreters](https://craftinginterpreters.com)__* book. 

### Prerequisites
To run this Lox interpreter, it is necessary to have a version of python **_3.5.x_** or higher,
installed and properly configured on your virtual machine. 
You can check your installed **_python3_** version number, by simply typing at the command prompt:
```
$ python3 --version
```
If any error, please consult the [Python documentation](https://docs.python.org/3/using/index.html) 
to proceed to the Python setup guide. 

### Running Tests

The Lox interpreter needs to obtain the source code from a given file or from a command prompt, line by line.
To run your Lox script in an interative prompt mode, type:
```
$ python3 PyLox.py
> ...
```
Or to interpret a script located in a *__.lox__* extension file, provide the full path to the file: 
```
$ python3 PyLox.py <file path>
```
You can try to run your own lox scripts or any of the scripts located in the _examples_ folder of this project.

**e.g.**, to run the *__example1.lox__* file, type:
```
$ python3 PyLox.py examples/example1.lox
```

### The Language

The Lox language, originally designed by [Bob Nystrom](https://github.com/munificent), 
is a **high-level dynamically typed language**, that supports OOP, and have a C-like syntax.

The dynamic type feature allows variables to store values of any type at runtime, 
but operations with operands of different data types are not allowed. 

#### Lox supports : 
    
    * 4 built-in data-types : Numbers, Booleans, Strings and nil,
    * Expressions,
    * Control Flow statements,
    * Print statement,
    * While and For Loops,
    * Functions,
    * Classes,
    * Single Inheritance 

### To Do

  - [ ] ternary operator ?:
  - [ ] remainder operator %
  - [ ] comma operator ,
  - [ ] anonymous functions 
  - [ ] break & continue statements
  - [ ] exit statement
  - [ ] delete statement
  - [ ] getters
  - [ ] allows to read input from user
  - [ ] ? allows to work with files
  - [ ] ? assignments += -= *= /= 
  - [ ] ? static methods
  - [ ] ? some other built-in data-types or functions
    ... 

### Status

*Finished Part II - A Tree-Walk Interpreter*

