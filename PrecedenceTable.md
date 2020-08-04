## PyLox Operator Precedence Table


| Precedence | Operator |          Description         | Associativity |
|:----------:|:--------:|:----------------------------:|:-------------:|
|    **1**   |    ()    |         Function call        | Left-to-right |
|    **1**   |     .    |      Class member access     | Left-to-right |
|    **2**   |     !    |          Logical not         | Right-to-left |
|    **2**   |     -    |          Unary minus         | Right-to-left |
|    **3**   |     *    |        Multiplication        | Left-to-right |
|    **3**   |     /    |           Division           | Left-to-right |
|    **3**   |     %    |           Remainder          | Left-to-right |
|    **4**   |     +    |            Addition          | Left-to-right |
|    **4**   |     -    |          Subtraction         | Left-to-right |
|    **5**   |   < <=   | relational operators < and ≤ | Left-to-right |
|    **5**   |   > >=   | relational operators > and ≥ | Left-to-right |
|    **6**   |   == !=  |      relational = and ≠      | Left-to-right |
|    **7**   |    and   |          Logical AND         | Left-to-right |
|    **8**   |    or    |          Logical OR          | Left-to-right |
|    **9**   |    ?:    |      Ternary Conditional     | Left-to-right |
|   **10**   |     =    |       Simple Assignment      | Right-to-left |
|   **11**   |     ,    |             Comma            | Left-to-right |
