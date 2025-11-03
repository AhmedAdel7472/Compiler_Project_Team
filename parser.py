# D7K Parser + AST (Recursive Descent)
from dataclasses import dataclass
from typing import List, Optional, Any

# ---------------------------
# Minimal Token class for demo (match your scanner)
# ---------------------------
@dataclass
class Token:
    type: str     # e.g., 'KEYWORD', 'IDENTIFIER', 'NUMBER', 'STRING', 'SYMBOL', 'RELOP', 'EOF'
    lexeme: str   # raw text (e.g., 'd7ktba3a', 'int', 'x', '42', '(', ';', '==')
    line: int = 0

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}')"

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

    # prepare prefix for children
    prefix += "    " if is_last else "│   "

    child_count = len(node.children)
    for i, child in enumerate(node.children):
        pretty_print(child, prefix, i == child_count - 1)

# ---------------------------
# Parser
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

    def advance(self) -> Token:
        tok = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def match_lexeme(self, expected: str) -> Token: # for terminals
        tok = self.current()
        if tok.lexeme == expected:
            return self.advance()
        raise ParserError(f"Expected lexeme '{expected}' but got {tok} at pos {self.pos}")

    def match_type(self, expected_type: str) -> Token:  # for non-terminals
        tok = self.current()
        if tok.type == expected_type:
            return self.advance()
        raise ParserError(f"Expected token type {expected_type} but got {tok} at pos {self.pos}")

    def accept(self, lexemes: List[str]) -> Optional[Token]: # for terminals
        tok = self.current()
        if tok.lexeme in lexemes:
            return self.advance()
        return None

    def accept_type(self, types: List[str]) -> Optional[Token]: # for non-terminals
        tok = self.current()
        if tok.type in types:
            return self.advance()
        return None

    def eof(self):
        return self.current().type == "EOF" or self.current().lexeme == "EOF"


    def parse(self) -> ASTNode:     # the program entry point
        root = ASTNode("Program")
        stmt_list = self.statement_list()
        root.add(stmt_list)
        if not self.eof():
            raise ParserError(f"Expected EOF but got {self.current()}")
        return root


    def statement_list(self) -> ASTNode:
        node = ASTNode("StatementList")
        # stop conditions: EOF or closing brace '}' (end of block)
        while not self.eof() and self.current().lexeme != '}':
            
            # empty statement (just a semicolon)
            if self.current().lexeme == ';':
                self.advance()
                continue
            stmt = self.statement()
            if stmt is None:
                # If parser couldn't parse a statement: error
                raise ParserError(f"Unexpected token in statement list: {self.current()}")
            node.add(stmt)
        return node

    # ---------- Statement ----------
    def statement(self) -> ASTNode:
        tok = self.current()

        # Declaration: data type token then identifier
        if tok.type == "DATATYPE" or (tok.type == "KEYWORD" and tok.lexeme in ["d7krkm","d7k34ry","d7kmslsl","d7kmntk","d7khrf"]):
            return self.declaration()

        # If token is identifier => assignment
        if tok.type == "IDENTIFIER":
            return self.assignment()

        # control keywords (D7K)
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

        # epsilon? If none matched, error
        raise ParserError(f"Unknown statement start: {tok} at pos {self.pos}")

    # ---------- Declarations ----------
    def declaration(self) -> ASTNode:
        # datatype
        dtype_tok = self.advance()  # consumed datatype token
        dtype = dtype_tok.lexeme
        # identifier
        id_tok = self.match_type("IDENTIFIER")
        self.match_lexeme("=")
        expr_node = self.expr()
        self.match_lexeme(";")
        node = ASTNode("Declaration", dtype)
        node.add(ASTNode("Identifier", id_tok.lexeme))
        node.add(expr_node)
        return node

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
        # optional else
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
        # RelOp expected
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

    # ---------- Expressions (Expr / Term / Factor) ----------
    def expr(self) -> ASTNode:
        # handle left-associative chain Term ((+|-) Term)*
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

# ---------------------------
# Example usage / demo
# ---------------------------
if __name__ == "__main__":
    # Example source (as tokens). Replace with tokens produced by your scanner.
    # Example D7K fragment:
    # int x = 5;
    # d7ktba3a(x);
    tokens = [
        Token("COMMENT", "#d7khaaat"),

        Token("DATATYPE", "d7krkm"),
        Token("IDENTIFIER", "score"),
        Token("SYMBOL", "="),
        Token("NUMBER", "102"),
        Token("SYMBOL", ";"),

        Token("KEYWORD", "d7klo"),
        Token("SYMBOL", "("),
        Token("IDENTIFIER", "score"),
        Token("RELOP", ">"),
        Token("NUMBER", "100"),
        Token("SYMBOL", ")"),
        Token("SYMBOL", "{"),

        Token("KEYWORD", "d7ktba3a"),
        Token("SYMBOL", "("),
        Token("STRING", "MVP performance!"),
        Token("SYMBOL", ")"),
        Token("SYMBOL", ";"),

        Token("SYMBOL", "}"),

        Token("KEYWORD", "d7k8er"),
        Token("SYMBOL", "{"),

        Token("KEYWORD", "d7ktba3a"),
        Token("SYMBOL", "("),
        Token("STRING", "Keep training!"),
        Token("SYMBOL", ")"),
        Token("SYMBOL", ";"),

        Token("SYMBOL", "}"),

        Token("KEYWORD", "d7krg3"),
        Token("NUMBER", "0"),
        Token("SYMBOL", ";"),

        Token("EOF", "EOF"),
    ]

    parser = Parser(tokens)
    ast = parser.parse()
    pretty_print(ast)
