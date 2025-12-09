# 😂 D7K Language

## 🚀 Project Overview

This project implements a mini compiler for a fictional programming language called D7K.
It includes the first three stages of compilation:

1. Lexical Analysis (Scanner)
2. Syntax Analysis (Parser)
3. Semantic Analysis

### 🔑 **Keywords**

| D7K Keyword | Meaning / Subtype                   |
| ----------- | ----------------------------------- |
| `d7ktba3a`  | OUTPUT (print statement)            |
| `d7ked5al`  | INPUT (read user input)             |
| `d7klo`     | IF_STATEMENT                        |
| `d7k8er`    | ELSE_BLOCK                          |
| `d7kdw5ny`  | WHILE_LOOP                          |
| `d7klf`     | FOR_LOOP                            |
| `d7krg3`    | RETURN_STATEMENT                    |
| `d7kbdaya`  | Main_function (program entry point) |
| `d7kmslsl`  | Define a string                     |
| `d7krqm`    | Define a number type                |
| `d7kmntq`   | Define a bool type                  |
| `d7k34ry`   | Define a decimal type               |

### **Parser Grammer**

Terminals are written as their lexemes (e.g., 'd7kbdaya', '{', ';').
Non-terminals are in CapitalizedNames.

Program
-> MainFunction EOF

MainFunction
-> 'd7kbdaya' '(' ')' Block

Block
-> '{' StatementList '}'

StatementList
-> { Statement }

Statement
-> VarDecl
| Assignment ';'
| IfStmt
| WhileStmt
| ForStmt
| OutputStmt ';'
| InputStmt ';'
| ReturnStmt ';'

VarDecl
-> Type IDENT ( '=' Expr )? ';'

Type
-> 'd7krqm' // number (integer or float)
| 'd7k34ry' // decimal
| 'd7kmslsl' // string
| 'd7kmntq' // bool

Assignment
-> IDENT '=' Expr

IfStmt
-> 'd7klo' '(' Expr ')' Block ['d7k8er' Block]

WhileStmt
-> 'd7kdw5ny' '(' Expr ')' Block

ForStmt
-> 'd7klf' '(' Assignment ';' Expr ';' Assignment ')' Block

OutputStmt
-> 'd7ktba3a' '(' Expr ')'

InputStmt
-> 'd7ked5al' '(' IDENT ')'

ReturnStmt
-> 'd7krg3' [Expr]

Expr
-> Equality

Equality
-> Relational { ('==' | '!=') Relational }

Relational
-> Add { ('<' | '>' | '<=' | '>=') Add }

Add
-> Mul { ('+' | '-') Mul }

Mul
-> Primary { ('\*' | '/') Primary }

Primary
-> NUMBER
| STRING
| BOOL_LITERAL // 'true' | 'false'
| IDENT
| '(' Expr ')'
