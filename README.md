## PyLox
A Tree-Walk Interpreter to the PyLox language, using the good old python for the simplest and cleanest implementation.

### Prerequisites
To run this PyLox interpreter, you will need to have a version of python higher or equal to **_3.5_** on your system. 
You can check your installed **_python3_** version, by typing at the command prompt:
```
$ make check
```
If any error, or a lower version, please consult the [Python documentation](https://docs.python.org/3/using/index.html) 
to proceed to the Python setup guide. 

### Running Tests

To run any PyLox script in an interative prompt mode, type:
```
$ make repl
> ...
```
Or to interpret a script located at a *__.plox__* file, provide the full path to the file: 
```
$ make run <file path>
```
You can try to run your own PyLox scripts, or any of the scripts located at the "_tests_" folder in this project.

**e.g.**, to run a single test script, type:
```
$ make test
```
Or to consult this guide at any time, type:

```
$ make help
```

### The Language

PyLox was born from the Lox language, originally designed by [Bob Nystrom](https://github.com/munificent) at the *__[Crafting Interpreters](https://craftinginterpreters.com)__* book. 

It is a **high-level dynamically-typed language**, that supports Object-Oriented Programming and have a C-like syntax.
This dynamic type feature allows variables to store values of any type at runtime, 
but operations with operands of different data types are not allowed.

#### PyLox supports : 
    
    * 4 built-in data-types : Numbers, Booleans, Strings and nil,
    * Expressions,
    * Control Flow statements,
    * Print statement,
    * While and For Loops,
    * Functions,
    * Classes,
    * Single Inheritance 
    
   
   ***please consult the PyLox Grammar file for more details**

### To Do
  - [ ] anonymous functions 
  - [x] break & continue statements
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


