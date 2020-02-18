## PyLox
A Python implementation, for study purposes, of the __Lox__ scripting language, based on the *__[Crafting Interpreters](https://craftinginterpreters.com)__* book. 
Currently, I am still working on its implementation, following Bob's tutorial, but I plan to finish soon.

### Prerequisites
To properly run this basic Lox interpreter with all its features, you will need to have any version of python __3.x.x__ installed and correctly configured on your virtual machine. 
You can see if you have **_python3_** installed by typing the following command line in your terminal :
```
$ python3 --version
```
It returned to me, ```Python 3.6.8```, which is my current working version of python for this project. 
If it returns an error message to you, please consult the [Python's documentation](https://docs.python.org/3/using/index.html) to proceed to the Python installation guide. 
All set then, let's move on. 

### Running Tests

Basically, until now, the interpreter can be executed in two ways, obtaining the source code of a given file, or from a command prompt line-by-line. To run your Lox script in an interative prompt mode, type:
```
$ python3 PyLox.py
> ...
```
Or to interpret a script located in a *__.lox__* file, provide the full path to the file: 
```
$ python3 PyLox.py <file path>
```
You can try to run the example.lox file in this project, by typing:
```
$ python3 PyLox.py example.lox
```
Here, the example.lox file is in the same directory as PyLox, so we don't need to specify its location.
