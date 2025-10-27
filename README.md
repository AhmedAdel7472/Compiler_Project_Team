# 🏀 BallScript Token Scanner

A **lexical analyzer (scanner)** built in Python for a fictional programming language called **BallScript**.  
This tool scans source code and identifies different types of tokens such as keywords, data types, symbols, strings, and comments — just like the first stage of a compiler.

---

## 🚀 Project Overview

The **BallScript Token Scanner** reads a `.txt` source file (default: `example.txt`) line by line, uses **regular expressions** to match token patterns, and classifies each match into categories and subtypes.

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

## 🏷️ BallScript Keywords and Data Types

### 🔑 **Keywords**

| BallScript Keyword | Meaning / Subtype |
|--------------------|-------------------|
| `d7kdlal`          | FUNCTION_DEF (used to define a function) |
| `d7ktba3a`         | OUTPUT (print statement) |
| `d7ked5al`         | INPUT (read user input) |
| `d7klo`            | IF_STATEMENT |
| `d7k8er`           | ELSE_BLOCK |
| `d7kdw5ny`         | WHILE_LOOP |
| `d7klf`            | FOR_LOOP |
| `d7krg3`           | RETURN_STATEMENT |
| `d7kkml`           | UNKNOWN / placeholder keyword |
| `#d7khaaat`        | IMPORT_LIB (used to include libraries) |
| `d7kspaace`        | NAMESPACE (define a scope or module) |
| `main`             | Main_function (program entry point) |
| `d7khrf` | Single character — “a play symbol or code.” |
---

###
