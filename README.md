# 😂 D7K Token Scanner

A **lexical analyzer (scanner)** built in Python for a fictional programming language called **D7K**.  
This tool scans source code and identifies different types of tokens such as keywords, data types, symbols, strings, and comments — just like the first stage of a compiler.

---

## 🚀 Project Overview

The **D7K Token Scanner** reads a `.txt` source file (default: `example.txt`) line by line, uses **regular expressions** to match token patterns, and classifies each match into categories and subtypes.

It’s part of the **Compiler_Project**, demonstrating how lexical analysis works during the compilation process.

---

## 🧠 Features

✅ Detects **keywords**, **data types**, **symbols**, **comments**, and **strings**  
✅ Uses **regular expressions** (`re` module) for pattern matching  
✅ Prints detailed output showing:

- Line number
- Token category (e.g., `KEYWORD`, `DATA_TYPE`)
- Subtype (e.g., `IF_STATEMENT`, `INTEGER_TYPE`)
- Actual matched value

✅ Easily extensible — just add new patterns or token types in the `TOKENS` and `TOKEN_TYPES` dictionaries

---

## 🏷️ D7K Keywords and Data Types

### 🔑 **Keywords**

| D7K Keyword | Meaning / Subtype                           |
| ----------- | ------------------------------------------- |
| `d7ktba3a`  | OUTPUT (print statement)                    |
| `d7ked5al`  | INPUT (read user input)                     |
| `d7klo`     | IF_STATEMENT                                |
| `d7k8er`    | ELSE_BLOCK                                  |
| `d7kdw5ny`  | WHILE_LOOP                                  |
| `d7klf`     | FOR_LOOP                                    |
| `d7krg3`    | RETURN_STATEMENT                            |
| `d7kkml`    | UNKNOWN / placeholder keyword               |
| `#d7khaaat` | IMPORT_LIB (used to include libraries)      |
| `d7kspaace` | NAMESPACE (define a scope or module)        |
| `main`      | Main_function (program entry point)         |
| `d7k7rf`    | Single character — “a play symbol or code.” |



### **Parser Grammer**

D7K Language Grammar (based on your current code)
Non-Terminal	Grammar
Program →	StatementList EOF
StatementList →	Statement StatementList | ε
Statement →	ImportStmt | UsingNamespaceStmt | FunctionDef | Declaration | Assignment | CallStmt | IfStmt | WhileStmt | ForStmt | ReturnStmt | OutputStmt | InputStmt
ImportStmt →	d7kimport Identifier ; | d7kimport < Identifier > ;
UsingNamespaceStmt →	using namespace Identifier ;
FunctionDef →	(DATATYPE | d7kdlal | main) Identifier ( Params ) { StatementList }
Params →	Param , Params | Param | ε
Param →	DATATYPE Identifier
Declaration →	DATATYPE Identifier = Expr ; | DATATYPE Identifier ;
Assignment →	Identifier = Expr ;
CallStmt →	Identifier ( ArgList ) ;
ArgList →	Expr , ArgList | Expr | ε
IfStmt →	d7klo ( Condition ) { StatementList } | d7klo ( Condition ) { StatementList } d7k8er { StatementList }
WhileStmt →	d7kdw5ny ( Condition ) { StatementList }
ForStmt →	d7klf ( Declaration Condition ; Assignment ) { StatementList }
ReturnStmt →	d7krg3 Expr ;
OutputStmt →	d7ktba3a ( Expr ) ;
InputStmt →	d7ked5al ( Identifier ) ;
Condition →	Expr RelOp Expr
Expr →	Expr + Term | Expr - Term | Term
Term →	Term * Factor | Term / Factor | Factor
Factor →	NUMBER | STRING | Identifier | ( Expr )
RelOp →	== | != | < | > | <= | >=



not handeled yet 
Documentation
Scanner old code return before writing the new code and makhlouf updates it done    
And we go to sleep 3ashan ayman 3ayez ynam done
w ana 3ayez ashtry men ta7t w ayman bardo done
function done
importing libraries done 
int main done
namespace std; done

Grammer docs in each function so if we want to update the grammar again later 
