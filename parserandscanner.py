#!/usr/bin/env python3
# d7k_compiler.py
import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Any

# ---------------------------
# Token class
# ---------------------------
@dataclass
class Token:
    type: str     # e.g., 'KEYWORD', 'IDENTIFIER', 'NUMBER', 'STRING', 'SYMBOL', 'RELOP', 'EOF', 'PREPROCESSOR', 'DATATYPE'
    lexeme: str   # raw text (e.g., 'd7ktba3a', 'int', 'x', '42', '(', ';', '==')
    line: int = 0

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}')"

# ---------------------------
# Scanner (option 2 style, pattern-based)
# ---------------------------

# Reserved words (D7K + C-like additions)
DATATYPES = {"d7krkm", "d7k34ry", "d7kmslsl", "d7kmntk", "d7khrf"}
KEYWORDS = {
    "d7ktba3a", "d7ked5al", "d7klo", "d7k8er",
    "d7kdw5ny", "d7klf", "d7krg3", "d7kspaace", "main", "d7kkml",
    "using", "namespace"
}
PREPROCESSORS = {"d7kimport"}

# Patterns: order matters (longer tokens first)
SCANNER_PATTERNS = [
    ("WHITESPACE", re.compile(r'[ \t\r\n]+')),
    ("COMMENT", re.compile(r'//[^\n]*')),                # line comment
    ("COMMENT", re.compile(r'/\*[\s\S]*?\*/')),          # block comment
    ("COMMENT", re.compile(r'\#[A-Za-z_]\w*')),          # pound-style like #d7khaaat
    ("PREPROCESSOR", re.compile(r'd7kimport\b')),        # d7kimport keyword
    ("STRING", re.compile(r'"([^"\\\n]|\\.)*"')),        # double-quoted strings
    ("STRING", re.compile(r"'([^'\\\n]|\\.)*'")),        # single-quoted strings
    # relational operators
    ("RELOP", re.compile(r'==|!=|<=|>=|<|>')),
    # increment/decrement or other two-char symbols
    ("SYMBOL", re.compile(r'\+\+|--')),
    # single-char symbols / operators (assignment "=" is SYMBOL)
    ("SYMBOL", re.compile(r'[=;{}\(\)\[\]\+\-\*/<>,]')),  # include < > , for include forms
    # numbers (integer/float)
    ("NUMBER", re.compile(r'\d+(\.\d+)?')),
    # identifiers / keywords / datatypes: letters, digits, underscores, starting with letter or underscore
    ("IDENTIFIER", re.compile(r'[A-Za-z_]\w*')),
]

def scan_source(source: str) -> List[Token]:
    """
    Scan the entire source string and return a flat list of Token objects.
    Pattern-based scanner: tries patterns at the current position, first match wins.
    """
    tokens: List[Token] = []
    pos = 0
    line = 1
    src_len = len(source)

    while pos < src_len:
        match = None
        matched_name = None
        for name, patt in SCANNER_PATTERNS:
            m = patt.match(source, pos)
            if m:
                match = m
                matched_name = name
                break

        if not match:
            context = source[pos:pos+20].replace("\n", "\\n")
            raise SyntaxError(f"Scanner: unexpected character at pos {pos} (line {line}): {context!r}")

        lexeme = match.group()
        # update line count based on matched text
        line += lexeme.count("\n")

        if matched_name == "WHITESPACE":
            pass  # skip
        elif matched_name == "COMMENT":
            tokens.append(Token("COMMENT", lexeme, line))
        elif matched_name == "PREPROCESSOR":
            # emit as PREPROCESSOR token (e.g., d7kimport)
            tokens.append(Token("PREPROCESSOR", lexeme, line))
        elif matched_name == "STRING":
            # store inner content (strip quotes)
            if lexeme.startswith('"') and lexeme.endswith('"') or lexeme.startswith("'") and lexeme.endswith("'"):
                inner = lexeme[1:-1]
            else:
                inner = lexeme
            tokens.append(Token("STRING", inner, line))
        elif matched_name == "NUMBER":
            tokens.append(Token("NUMBER", lexeme, line))
        elif matched_name == "IDENTIFIER":
            lw = lexeme
            if lw in DATATYPES:
                tokens.append(Token("DATATYPE", lw, line))
            elif lw in KEYWORDS:
                tokens.append(Token("KEYWORD", lw, line))
            elif lw in PREPROCESSORS:
                tokens.append(Token("PREPROCESSOR", lw, line))
            else:
                tokens.append(Token("IDENTIFIER", lw, line))
        elif matched_name == "RELOP":
            tokens.append(Token("RELOP", lexeme, line))
        elif matched_name == "SYMBOL":
            tokens.append(Token("SYMBOL", lexeme, line))
        else:
            tokens.append(Token(matched_name, lexeme, line))

        pos = match.end()

    tokens.append(Token("EOF", "EOF", line))
    return tokens

# Give the file content to scan_source which returns tokens
def scan_file(filename: str) -> List[Token]:
    with open(filename, "r", encoding="utf-8") as f:
        source = f.read()
    return scan_source(source)

# ---------------------------
# AST Node definitions
# ---------------------------
class ASTNode:
    def __init__(self, node_type: str, value: Optional[Any] = None, children: Optional[List['ASTNode']] = None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

    def add(self, node: 'ASTNode'):
        self.children.append(node)

    def __repr__(self):
        if self.value is not None and not self.children:
            return f"{self.node_type}({self.value})"
        elif self.value is None and not self.children:
            return f"{self.node_type}"
        else:
            return f"{self.node_type}({self.value}, children={len(self.children)})"

def pretty_print(node: ASTNode, prefix: str = "", is_last: bool = True):
    connector = "└── " if is_last else "├── "
    print(prefix + connector + (f"{node.node_type}: {node.value}" if node.value is not None else node.node_type))
    prefix += "    " if is_last else "│   "
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        pretty_print(child, prefix, i == child_count - 1)

# ---------------------------
# Parser (recursive descent)
# ---------------------------
class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ---------- utilities ----------
    def current(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token("EOF", "EOF")

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else Token("EOF", "EOF")

    def advance(self) -> Token:
        tok = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def match_lexeme(self, expected: str) -> Token:
        tok = self.current()
        if tok.lexeme == expected:
            return self.advance()
        raise ParserError(f"Expected lexeme '{expected}' but got {tok} at pos {self.pos}")

    def match_type(self, expected_type: str) -> Token:
        tok = self.current()
        if tok.type == expected_type:
            return self.advance()
        raise ParserError(f"Expected token type {expected_type} but got {tok} at pos {self.pos}")

    def accept(self, lexemes: List[str]) -> Optional[Token]:
        tok = self.current()
        if tok.lexeme in lexemes:
            return self.advance()
        return None

    def accept_type(self, types: List[str]) -> Optional[Token]:
        tok = self.current()
        if tok.type in types:
            return self.advance()
        return None

    def eof(self):
        return self.current().type == "EOF" or self.current().lexeme == "EOF"

    # ---------- entry ----------
    def parse(self) -> ASTNode:
        root = ASTNode("Program")
        stmt_list = self.statement_list()
        root.add(stmt_list)
        if not self.eof():
            raise ParserError(f"Expected EOF but got {self.current()}")
        return root

    def statement_list(self) -> ASTNode:
        node = ASTNode("StatementList")
        while not self.eof() and self.current().lexeme != '}':
            if self.current().lexeme == ';':
                self.advance()
                continue
            stmt = self.statement()
            node.add(stmt)
        return node

    # ---------- top-level statements ----------
    def statement(self) -> ASTNode:
        tok = self.current()

        # Preprocessor import: d7kimport IDENTIFIER ;
        if tok.type == "PREPROCESSOR":
            return self.import_stmt()

        # using namespace std;
        if tok.type == "KEYWORD" and tok.lexeme == "using":
            return self.using_namespace_stmt()

        if tok.type == "DATATYPE" or (tok.type == "KEYWORD" and tok.lexeme in ["d7krkm","d7k34ry","d7kmslsl","d7kmntk","d7khrf"]):
            # disambiguate: if after datatype + identifier comes '(' then it's a function
            next_tok = self.peek()
            next2_tok = self.peek(2)
            if next_tok.type == "IDENTIFIER" and next2_tok.lexeme == "(":
                return self.function_def()
            return self.declaration()

        # assignment
        if tok.type == "IDENTIFIER":
            # If next lexeme is '(' then it's a function call statement (e.g., foo();)
            if self.peek().lexeme == "(":
                return self.call_stmt()
            return self.assignment()

        # control keywords (existing)
        if tok.lexeme == "d7klo":
            return self.if_stmt()
        if tok.lexeme == "d7kdw5ny":
            return self.while_stmt()
        if tok.lexeme == "d7klf":
            return self.for_stmt()
        if tok.lexeme == "d7krg3":  # return
            return self.return_stmt()
        if tok.lexeme == "d7ktba3a":  # output
            return self.output_stmt()
        if tok.lexeme == "d7ked5al":  # input
            return self.input_stmt()
        if tok.type == "COMMENT":
            c = ASTNode("Comment", self.current().lexeme)
            self.advance()
            return c

        raise ParserError(f"Unknown statement start: {tok} at pos {self.pos}")

    # ---------- Import ----------
    def import_stmt(self) -> ASTNode:
        p = self.match_type("PREPROCESSOR")  # d7kimport
        # accept either <iostream> or identifier
        lib_tok = self.current()
        if lib_tok.lexeme == "<":
            # parse < name >
            self.match_lexeme("<")
            name_tok = self.match_type("IDENTIFIER")
            self.match_lexeme(">")
            self.match_lexeme(";")
            node = ASTNode("Import", name_tok.lexeme)
            return node
        else:
            # simple identifier import: d7kimport iostream;
            name_tok = self.match_type("IDENTIFIER")
            self.match_lexeme(";")
            node = ASTNode("Import", name_tok.lexeme)
            return node

    # ---------- Using namespace ----------
    def using_namespace_stmt(self) -> ASTNode:
        self.match_lexeme("using")
        self.match_lexeme("namespace")
        ns_tok = self.match_type("IDENTIFIER")
        self.match_lexeme(";")
        node = ASTNode("UsingNamespace", ns_tok.lexeme)
        return node

    # # ---------- Function definition ----------
    def function_def(self) -> ASTNode:
        """
        Handles:
            DATATYPE IDENTIFIER ( params ) { body }
            d7kdlal IDENTIFIER ( params ) { body }
            KEYWORD main ( ) { body }
        Very small params support: parse zero or comma-separated identifiers (no types).
        """
        # optional return type
        ret_type = None
        if self.current().type == "DATATYPE" and self.current().lexeme != "main":
            ret_type = self.advance().lexeme
        elif self.current().type == "KEYWORD" and self.current().lexeme == "main":
            # main with implicit return type
            ret_type = "implicit"
        # now expect identifier (function name) or 'main' is already keyword
        name_tok = None
        if self.current().type == "IDENTIFIER":
            name_tok = self.advance()
        elif self.current().type == "KEYWORD" and self.current().lexeme == "main":
            name_tok = self.advance()
        else:
            raise ParserError(f"Expected function name but got {self.current()} at pos {self.pos}")

        # params
        self.match_lexeme("(")
        params = []
        while self.current().lexeme != ")":
            # parse a parameter: type + identifier
            param_type = self.match_type("DATATYPE")
            param_name = self.match_type("IDENTIFIER")
            
            p_node = ASTNode("Param", f"{param_type.lexeme} {param_name.lexeme}")
            p_node.add(ASTNode("Type", param_type.lexeme))
            p_node.add(ASTNode("Identifier", param_name.lexeme))
            params.append(p_node)
                    

            if self.current().lexeme == ",":
                self.match_lexeme(",")  # skip comma and continue
                continue
            break
        self.match_lexeme(")")


        # body
        self.match_lexeme("{")
        body = self.statement_list()
        self.match_lexeme("}")

        node = ASTNode("Function", f"{name_tok.lexeme} : {ret_type}")
        # params node
        params_node = ASTNode("Params")
        for p in params:
            params_node.add(ASTNode("Param", p))
        node.add(params_node)
        # body node (inline the statements)
        node.add(ASTNode("Body", children=body.children))
        return node

    # ---------- Call statement (simple) ----------
    def call_stmt(self) -> ASTNode:
        name_tok = self.match_type("IDENTIFIER")
        self.match_lexeme("(")
        # simple argument list using expressions
        args = []
        if self.current().lexeme != ")":
            args.append(self.expr())
            while self.current().lexeme == ",":
                self.match_lexeme(",")
                args.append(self.expr())
        self.match_lexeme(")")
        self.match_lexeme(";")
        node = ASTNode("Call", name_tok.lexeme)
        for a in args:
            node.add(a)
        return node

    def declaration(self) -> ASTNode:
        # read datatype first
        dtype_tok = self.match_type("DATATYPE")
        dtype = dtype_tok.lexeme

        # second token MUST be identifier (var name or func name)
        if self.current().type not in ("IDENTIFIER", "KEYWORD"):
            raise ParserError(f"Expected identifier after datatype {dtype} but got {self.current()}")

        id_tok = self.advance()

        # IMPORTANT FIX:
        # check if this is actually a function declaration BEFORE normal variable declaration
        # int main (...)
        if self.current().lexeme == "(":
            return self.function_declaration(dtype_tok, id_tok)

        # variable declaration with init: int x = expr;
        if self.current().lexeme == "=":
            self.match_lexeme("=")
            expr_node = self.expr()
            self.match_lexeme(";")
            node = ASTNode("Declaration", dtype)
            node.add(ASTNode("Identifier", id_tok.lexeme))
            node.add(expr_node)
            return node

        # simple var declaration: int x;
        self.match_lexeme(";")
        node = ASTNode("Declaration", dtype)
        node.add(ASTNode("Identifier", id_tok.lexeme))
        return node
    
    def function_declaration(self, type_token, id_token):
        self.match_lexeme("(")

        params = []
        if self.current().lexeme != ")":
            params.append(self.param())
            while self.current().lexeme == ",":
                self.match_lexeme(",")
                params.append(self.param())

        self.match_lexeme(")")

        body = self.block()

        node = ASTNode("FunctionDecl", id_token.lexeme)
        node.add(ASTNode("ReturnType", type_token.lexeme))

        params_node = ASTNode("Params")
        for p in params:
            params_node.add(p)
        node.add(params_node)

        node.add(body)

        return node
    
    def param(self):
        dtype = self.match_type("DATATYPE")
        ident = self.match_type("IDENTIFIER")
        p = ASTNode("Param")
        p.add(ASTNode("Type", dtype.lexeme))
        p.add(ASTNode("Identifier", ident.lexeme))
        return p


    def block(self):
        self.match_lexeme("{")
        stmt_list = self.statement_list()
        self.match_lexeme("}")
        return ASTNode("Block", children=stmt_list.children)


    # ---------- Assignment ----------
    def assignment(self) -> ASTNode:
        id_tok = self.match_type("IDENTIFIER")
        self.match_lexeme("=")
        expr_node = self.expr()
        self.match_lexeme(";")
        node = ASTNode("Assignment")
        node.add(ASTNode("Identifier", id_tok.lexeme))
        node.add(expr_node)
        return node

    # ---------- If ----------
    def if_stmt(self) -> ASTNode:
        self.match_lexeme("d7klo")
        self.match_lexeme("(")
        cond = self.condition()
        self.match_lexeme(")")
        self.match_lexeme("{")
        then_block = self.statement_list()
        self.match_lexeme("}")
        node = ASTNode("If")
        node.add(cond)
        node.add(ASTNode("ThenBlock", children=then_block.children))
        if self.current().lexeme == "d7k8er":
            self.match_lexeme("d7k8er")
            self.match_lexeme("{")
            else_block = self.statement_list()
            self.match_lexeme("}")
            node.add(ASTNode("ElseBlock", children=else_block.children))
        return node

    # ---------- While ----------
    def while_stmt(self) -> ASTNode:
        self.match_lexeme("d7kdw5ny")
        self.match_lexeme("(")
        cond = self.condition()
        self.match_lexeme(")")
        self.match_lexeme("{")
        body = self.statement_list()
        self.match_lexeme("}")
        node = ASTNode("While")
        node.add(cond)
        node.add(ASTNode("Body", children=body.children))
        return node

    # ---------- For ----------
    def for_stmt(self) -> ASTNode:
        self.match_lexeme("d7klf")
        self.match_lexeme("(")
        # Declaration ; Condition ; Assignment
        decl = self.declaration()
        cond = self.condition()
        self.match_lexeme(";")
        assign = self.assignment()
        self.match_lexeme(")")
        self.match_lexeme("{")
        body = self.statement_list()
        self.match_lexeme("}")
        node = ASTNode("For")
        node.add(decl)
        node.add(cond)
        node.add(assign)
        node.add(ASTNode("Body", children=body.children))
        return node

    # ---------- Return ----------
    def return_stmt(self) -> ASTNode:
        self.match_lexeme("d7krg3")
        expr_node = self.expr()
        self.match_lexeme(";")
        node = ASTNode("Return")
        node.add(expr_node)
        return node

    # ---------- Output ----------
    def output_stmt(self) -> ASTNode:
        self.match_lexeme("d7ktba3a")
        self.match_lexeme("(")
        e = self.expr()
        self.match_lexeme(")")
        self.match_lexeme(";")
        node = ASTNode("Output")
        node.add(e)
        return node

    # ---------- Input ----------
    def input_stmt(self) -> ASTNode:
        self.match_lexeme("d7ked5al")
        self.match_lexeme("(")
        id_tok = self.match_type("IDENTIFIER")
        self.match_lexeme(")")
        self.match_lexeme(";")
        node = ASTNode("Input")
        node.add(ASTNode("Identifier", id_tok.lexeme))
        return node

    # ---------- Condition ----------
    def condition(self) -> ASTNode:
        left = self.expr()
        rel = self.current()
        if rel.type == "RELOP" or rel.lexeme in ["==", "!=", "<", ">", "<=", ">="]:
            self.advance()
        else:
            raise ParserError(f"Expected relational operator but got {rel}")
        right = self.expr()
        node = ASTNode("Condition")
        node.add(left)
        node.add(ASTNode("RelOp", rel.lexeme))
        node.add(right)
        return node

    # ---------- Expressions ----------
    def expr(self) -> ASTNode:
        node = self.term()
        while self.current().lexeme in ["+", "-"]:
            op = self.advance().lexeme
            right = self.term()
            new = ASTNode("BinaryOp", op)
            new.add(node)
            new.add(right)
            node = new
        return node

    def term(self) -> ASTNode:
        node = self.factor()
        while self.current().lexeme in ["*", "/"]:
            op = self.advance().lexeme
            right = self.factor()
            new = ASTNode("BinaryOp", op)
            new.add(node)
            new.add(right)
            node = new
        return node

    def factor(self) -> ASTNode:
        tok = self.current()
        if tok.type == "NUMBER":
            self.advance()
            return ASTNode("Number", tok.lexeme)
        if tok.type == "STRING":
            self.advance()
            return ASTNode("String", tok.lexeme)
        if tok.type == "IDENTIFIER":
            self.advance()
            return ASTNode("Identifier", tok.lexeme)
        if tok.lexeme == "(":
            self.match_lexeme("(")
            node = self.expr()
            self.match_lexeme(")")
            return node
        raise ParserError(f"Unexpected factor token: {tok}")


def main():
    tokens = scan_file("example.txt")

    print("Tokens:")
    for t in tokens:
        print(" ", t)
    print("\nParsing...")
    parser = Parser(tokens)
    ast = parser.parse()
    print("\nAST:")
    pretty_print(ast)
    
    return 0


main()
