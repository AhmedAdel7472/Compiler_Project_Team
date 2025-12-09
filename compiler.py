#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import List, Optional, Any

# =======================
# TOKEN
# =======================

@dataclass
class Token:
    type: str   # IDENT, NUMBER, STRING, KEYWORD, DATATYPE, RELOP, SYMBOL, BOOL, EOF
    lexeme: str
    line: int

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', line={self.line})"


# =======================
# SCANNER
# =======================

DATATYPES = {"d7krqm", "d7k34ry", "d7kmslsl", "d7kmntq"}
KEYWORDS = {
    "d7ktba3a", "d7ked5al", "d7klo", "d7k8er",
    "d7kdw5ny", "d7klf", "d7krg3", "d7kbdaya"
}
BOOL_LITERALS = {"true", "false"}

SCANNER_PATTERNS = [
    ("WHITESPACE", re.compile(r'[ \t\r\n]+')),
    ("COMMENT",    re.compile(r'//[^\n]*')),
    ("STRING",     re.compile(r'"([^"\\\n]|\\.)*"')),
    ("RELOP",      re.compile(r'==|!=|<=|>=|<|>')),
    ("SYMBOL",     re.compile(r'[{}(),;=+\-*/]')),
    ("NUMBER",     re.compile(r'\d+(\.\d+)?')),
    ("IDENT",      re.compile(r'[A-Za-z_]\w*')),
]

def scan_source(source: str) -> List[Token]:
    tokens: List[Token] = []
    pos = 0
    line = 1
    n = len(source)

    while pos < n:
        match = None
        kind = None
        for name, pattern in SCANNER_PATTERNS:
            m = pattern.match(source, pos)
            if m:
                match = m
                kind = name
                break

        if not match:
            context = source[pos:pos+20].replace("\n", "\\n")
            raise SyntaxError(f"Unknown character at line {line}: {context!r}")

        text = match.group(0)
        line += text.count("\n")

        if kind in ("WHITESPACE", "COMMENT"):
            pass
        elif kind == "STRING":
            inner = text[1:-1]  # drop quotes
            tokens.append(Token("STRING", inner, line))
        elif kind == "NUMBER":
            tokens.append(Token("NUMBER", text, line))
        elif kind == "RELOP":
            tokens.append(Token("RELOP", text, line))
        elif kind == "SYMBOL":
            tokens.append(Token("SYMBOL", text, line))
        elif kind == "IDENT":
            if text in DATATYPES:
                tokens.append(Token("DATATYPE", text, line))
            elif text in KEYWORDS:
                tokens.append(Token("KEYWORD", text, line))
            elif text in BOOL_LITERALS:
                tokens.append(Token("BOOL", text, line))
            else:
                tokens.append(Token("IDENT", text, line))
        else:
            tokens.append(Token(kind, text, line))

        pos = match.end()

    tokens.append(Token("EOF", "EOF", line))
    return tokens

def scan_file(filename: str) -> List[Token]:
    with open(filename, "r", encoding="utf-8") as f:
        return scan_source(f.read())


# =======================
# AST NODE
# =======================

class ASTNode:
    def __init__(self, node_type: str, value: Optional[Any] = None, children: Optional[List['ASTNode']] = None):
        self.node_type = node_type
        self.value = value
        self.children: List[ASTNode] = children or []

    def add(self, node: 'ASTNode'):
        self.children.append(node)

    def __repr__(self):
        if self.children:
            return f"{self.node_type}({self.value}, children={len(self.children)})"
        else:
            return f"{self.node_type}({self.value})"


def pretty_print(node: ASTNode, prefix: str = "", is_last: bool = True):
    connector = "└── " if is_last else "├── "
    label = f"{node.node_type}"
    if node.value is not None:
        label += f": {node.value}"
    print(prefix + connector + label)
    prefix += "    " if is_last else "│   "
    for i, child in enumerate(node.children):
        pretty_print(child, prefix, i == len(node.children) - 1)


# =======================
# PARSER (Recursive Descent)
# =======================

class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token("EOF", "EOF", self.current().line)

    def advance(self) -> Token:
        tok = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def match_lexeme(self, lexeme: str):
        tok = self.current()
        if tok.lexeme == lexeme:
            return self.advance()
        raise ParserError(f"Expected '{lexeme}' but got {tok} at pos {self.pos}")

    def match_type(self, t: str):
        tok = self.current()
        if tok.type == t:
            return self.advance()
        raise ParserError(f"Expected type {t} but got {tok} at pos {self.pos}")

    def accept_lexeme(self, lexeme: str) -> Optional[Token]:
        tok = self.current()
        if tok.lexeme == lexeme:
            return self.advance()
        return None

    # ---- entry ----
    def parse(self) -> ASTNode:
        program = ASTNode("Program")

        # { FunctionDecl } MainFunction EOF
        while not (self.current().type == "KEYWORD" and self.current().lexeme == "d7kbdaya"):
            if self.current().type == "EOF":
                raise ParserError("Missing main function 'd7kbdaya'")
            program.add(self.function_decl())

        program.add(self.main_function())

        if self.current().type != "EOF":
            raise ParserError(f"Nothing allowed after main, got {self.current()}")
        return program

    # ---- function declarations ----
    def function_decl(self) -> ASTNode:
        # Type IDENT '(' ParamList? ')' Block
        ret_type_tok = self.match_type("DATATYPE")
        ret_type = ret_type_tok.lexeme
        name_tok = self.match_type("IDENT")
        name = name_tok.lexeme

        self.match_lexeme("(")
        params: List[ASTNode] = []
        if self.current().lexeme != ")":
            params.append(self.param())
            while self.accept_lexeme(","):
                params.append(self.param())
        self.match_lexeme(")")

        block = self.block()

        node = ASTNode("FunctionDecl", name)
        node.add(ASTNode("ReturnType", ret_type))
        params_node = ASTNode("Params")
        for p in params:
            params_node.add(p)
        node.add(params_node)
        node.add(block)
        return node

    def param(self) -> ASTNode:
        dtype_tok = self.match_type("DATATYPE")
        ident_tok = self.match_type("IDENT")
        p = ASTNode("Param")
        p.add(ASTNode("Type", dtype_tok.lexeme))
        p.add(ASTNode("Identifier", ident_tok.lexeme))
        return p

    def main_function(self) -> ASTNode:
        # d7kbdaya() Block
        tok = self.current()
        if not (tok.type == "KEYWORD" and tok.lexeme == "d7kbdaya"):
            raise ParserError(f"Expected 'd7kbdaya' for main, got {tok}")
        self.advance()
        self.match_lexeme("(")
        self.match_lexeme(")")
        block = self.block()
        node = ASTNode("MainFunc", "d7kbdaya")
        node.add(block)
        return node

    # ---- block & statements ----
    def block(self) -> ASTNode:
        self.match_lexeme("{")
        stmts = self.statement_list()
        self.match_lexeme("}")
        return ASTNode("Block", children=stmts.children)

    def statement_list(self) -> ASTNode:
        node = ASTNode("StatementList")
        while self.current().type != "EOF" and self.current().lexeme != "}":
            stmt = self.statement()
            node.add(stmt)
        return node

    def statement(self) -> ASTNode:
        tok = self.current()

        # VarDecl
        if tok.type == "DATATYPE":
            return self.vardecl()

        # Assignment (IDENT = ...)
        if tok.type == "IDENT":
            # could also be a function call as statement in future; for now, we treat calls only in expressions.
            return self.assignment_stmt()

        if tok.type == "KEYWORD":
            if tok.lexeme == "d7klo":
                return self.if_stmt()
            if tok.lexeme == "d7kdw5ny":
                return self.while_stmt()
            if tok.lexeme == "d7klf":
                return self.for_stmt()
            if tok.lexeme == "d7ktba3a":
                return self.output_stmt()
            if tok.lexeme == "d7ked5al":
                return self.input_stmt()
            if tok.lexeme == "d7krg3":
                return self.return_stmt()

        raise ParserError(f"Unexpected statement start: {tok}")

    def vardecl(self) -> ASTNode:
        dtype_tok = self.match_type("DATATYPE")
        dtype = dtype_tok.lexeme
        ident_tok = self.match_type("IDENT")
        name = ident_tok.lexeme

        node = ASTNode("VarDecl", dtype)
        node.add(ASTNode("Identifier", name))

        if self.accept_lexeme("="):
            expr = self.expr()
            node.add(expr)

        self.match_lexeme(";")
        return node

    def assignment_stmt(self) -> ASTNode:
        ident_tok = self.match_type("IDENT")
        name = ident_tok.lexeme
        self.match_lexeme("=")
        expr = self.expr()
        self.match_lexeme(";")
        node = ASTNode("Assign")
        node.add(ASTNode("Identifier", name))
        node.add(expr)
        return node

    def if_stmt(self) -> ASTNode:
        self.match_lexeme("d7klo")
        self.match_lexeme("(")
        cond = self.expr()
        self.match_lexeme(")")
        then_block = self.block()
        node = ASTNode("If")
        node.add(cond)
        node.add(then_block)

        if self.current().lexeme == "d7k8er":
            self.advance()
            else_block = self.block()
            node.add(else_block)
        return node

    def while_stmt(self) -> ASTNode:
        self.match_lexeme("d7kdw5ny")
        self.match_lexeme("(")
        cond = self.expr()
        self.match_lexeme(")")
        body = self.block()
        node = ASTNode("While")
        node.add(cond)
        node.add(body)
        return node

    def for_stmt(self) -> ASTNode:
        # d7klf ( Assignment ; Expr ; Assignment ) Block
        self.match_lexeme("d7klf")
        self.match_lexeme("(")
        init = self.assignment_stmt_no_semicolon()
        self.match_lexeme(";")
        cond = self.expr()
        self.match_lexeme(";")
        update = self.assignment_stmt_no_semicolon()
        self.match_lexeme(")")
        body = self.block()
        node = ASTNode("For")
        node.add(init)
        node.add(cond)
        node.add(update)
        node.add(body)
        return node

    def assignment_stmt_no_semicolon(self) -> ASTNode:
        ident_tok = self.match_type("IDENT")
        name = ident_tok.lexeme
        self.match_lexeme("=")
        expr = self.expr()
        node = ASTNode("Assign")
        node.add(ASTNode("Identifier", name))
        node.add(expr)
        return node

    def output_stmt(self) -> ASTNode:
        self.match_lexeme("d7ktba3a")
        self.match_lexeme("(")
        expr = self.expr()
        self.match_lexeme(")")
        self.match_lexeme(";")
        node = ASTNode("Output")
        node.add(expr)
        return node

    def input_stmt(self) -> ASTNode:
        self.match_lexeme("d7ked5al")
        self.match_lexeme("(")
        ident_tok = self.match_type("IDENT")
        self.match_lexeme(")")
        self.match_lexeme(";")
        node = ASTNode("Input")
        node.add(ASTNode("Identifier", ident_tok.lexeme))
        return node

    def return_stmt(self) -> ASTNode:
        self.match_lexeme("d7krg3")
        node = ASTNode("Return")
        if self.current().lexeme != ";":
            expr = self.expr()
            node.add(expr)
        self.match_lexeme(";")
        return node

    # ---- expressions ----
    def expr(self) -> ASTNode:
        return self.equality()

    def equality(self) -> ASTNode:
        node = self.relational()
        while self.current().type == "RELOP" and self.current().lexeme in ("==", "!="):
            op = self.advance().lexeme
            right = self.relational()
            node = ASTNode("BinaryOp", op, [node, right])
        return node

    def relational(self) -> ASTNode:
        node = self.add()
        while self.current().type == "RELOP" and self.current().lexeme in ("<", ">", "<=", ">="):
            op = self.advance().lexeme
            right = self.add()
            node = ASTNode("BinaryOp", op, [node, right])
        return node

    def add(self) -> ASTNode:
        node = self.mul()
        while self.current().lexeme in ("+", "-"):
            op = self.advance().lexeme
            right = self.mul()
            node = ASTNode("BinaryOp", op, [node, right])
        return node

    def mul(self) -> ASTNode:
        node = self.primary()
        while self.current().lexeme in ("*", "/"):
            op = self.advance().lexeme
            right = self.primary()
            node = ASTNode("BinaryOp", op, [node, right])
        return node

    def primary(self) -> ASTNode:
        tok = self.current()

        # NUMBER
        if tok.type == "NUMBER":
            self.advance()
            return ASTNode("NumberLiteral", tok.lexeme)

        # STRING
        if tok.type == "STRING":
            self.advance()
            return ASTNode("StringLiteral", tok.lexeme)

        # BOOL
        if tok.type == "BOOL":
            self.advance()
            return ASTNode("BoolLiteral", tok.lexeme)

        # IDENT / CallExpr
        if tok.type == "IDENT":
            # function call?
            if self.peek().lexeme == "(":
                name = tok.lexeme
                self.advance()  # IDENT
                self.match_lexeme("(")
                args: List[ASTNode] = []
                if self.current().lexeme != ")":
                    args.append(self.expr())
                    while self.accept_lexeme(","):
                        args.append(self.expr())
                self.match_lexeme(")")
                node = ASTNode("Call", name)
                for a in args:
                    node.add(a)
                return node
            else:
                self.advance()
                return ASTNode("Identifier", tok.lexeme)

        # ( Expr )
        if tok.lexeme == "(":
            self.advance()
            node = self.expr()
            self.match_lexeme(")")
            return node

        raise ParserError(f"Unexpected token in expression: {tok}")


# =======================
# SEMANTIC ANALYSIS
# =======================

class SemanticError(Exception):
    pass


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # list of dicts

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def declare(self, name: str, dtype: str):
        if name in self.scopes[-1]:
            raise SemanticError(f"Redeclaration of variable '{name}' in same scope")
        self.scopes[-1][name] = dtype

    def lookup(self, name: str) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SemanticError(f"Use of undeclared variable '{name}'")


class FunctionTable:
    def __init__(self):
        self.table = {}  # name -> (return_type, [param_types])

    def declare(self, name: str, ret_type: str, param_types: List[str]):
        if name in self.table:
            raise SemanticError(f"Redefinition of function '{name}'")
        self.table[name] = (ret_type, param_types)

    def lookup(self, name: str):
        if name not in self.table:
            raise SemanticError(f"Call to undeclared function '{name}'")
        return self.table[name]


class SemanticAnalyzer:
    def __init__(self, root: ASTNode):
        self.root = root
        self.symbols = SymbolTable()
        self.functions = FunctionTable()
        self.current_return_type: Optional[str] = None
        self.pending_params: Optional[List[tuple[str, str]]] = None  # (name, type)

    def analyze(self):
        self.visit(self.root)

    def visit(self, node: ASTNode):
        method = getattr(self, f"visit_{node.node_type}", self.visit_generic)
        return method(node)

    def visit_generic(self, node: ASTNode):
        for c in node.children:
            self.visit(c)

    # Program: children = FunctionDecl..., MainFunc
    def visit_Program(self, node: ASTNode):
        for child in node.children:
            self.visit(child)

    # FunctionDecl(name)
    def visit_FunctionDecl(self, node: ASTNode):
        name = node.value
        ret_type = node.children[0].value  # ReturnType
        params_node = node.children[1]
        body_block = node.children[2]

        param_types: List[str] = []
        param_pairs: List[tuple[str, str]] = []

        for p in params_node.children:
            ptype = p.children[0].value
            pname = p.children[1].value
            param_types.append(ptype)
            param_pairs.append((pname, ptype))

        # define function
        self.functions.declare(name, ret_type, param_types)

        # analyze body
        old_ret = self.current_return_type
        old_pending = self.pending_params
        self.current_return_type = ret_type
        self.pending_params = param_pairs  # will be declared at Block entry
        self.visit(body_block)
        self.current_return_type = old_ret
        self.pending_params = old_pending

    # MainFunc
    def visit_MainFunc(self, node: ASTNode):
        body_block = node.children[0]
        old_ret = self.current_return_type
        old_pending = self.pending_params
        self.current_return_type = None  # main has no return type
        self.pending_params = None
        self.visit(body_block)
        self.current_return_type = old_ret
        self.pending_params = old_pending

    # Block
    def visit_Block(self, node: ASTNode):
        self.symbols.push()
        # if this is a function body with parameters to declare
        if self.pending_params:
            for name, dtype in self.pending_params:
                self.symbols.declare(name, dtype)
            self.pending_params = None
        for stmt in node.children:
            self.visit(stmt)
        self.symbols.pop()

    # VarDecl(dtype)
    def visit_VarDecl(self, node: ASTNode):
        dtype = node.value
        name = node.children[0].value
        self.symbols.declare(name, dtype)
        if len(node.children) == 2:
            expr_type = self.visit(node.children[1])
            self._check_assign_compat(dtype, expr_type, f"initialization of '{name}'")

    # Assign
    def visit_Assign(self, node: ASTNode):
        name = node.children[0].value
        var_type = self.symbols.lookup(name)
        expr_type = self.visit(node.children[1])
        self._check_assign_compat(var_type, expr_type, f"assignment to '{name}'")

    def visit_Identifier(self, node: ASTNode):
        return self.symbols.lookup(node.value)

    def visit_NumberLiteral(self, node: ASTNode):
        if "." in node.value:
            return "d7k34ry"
        return "d7krqm"

    def visit_StringLiteral(self, node: ASTNode):
        return "d7kmslsl"

    def visit_BoolLiteral(self, node: ASTNode):
        return "d7kmntq"

    def visit_BinaryOp(self, node: ASTNode):
        op = node.value
        left_t = self.visit(node.children[0])
        right_t = self.visit(node.children[1])
        
        if op in ("+", "-", "*", "/"):
            if left_t not in ("d7krqm", "d7k34ry") or right_t not in ("d7krqm", "d7k34ry"):
                raise SemanticError(f"Operator '{op}' requires numeric operands, got {left_t} and {right_t}")
            if left_t == "d7k34ry" or right_t == "d7k34ry":
                return "d7k34ry"
            return "d7krqm"

        if op in ("<", ">", "<=", ">=", "==", "!="):
            if left_t != right_t:
                raise SemanticError(f"Comparison '{op}' with mismatched types {left_t} and {right_t}")
            return "d7kmntq"

        raise SemanticError(f"Unknown binary operator '{op}'")

    def visit_If(self, node: ASTNode):
        cond_type = self.visit(node.children[0])
        if cond_type != "d7kmntq":
            raise SemanticError(f"If condition must be bool (d7kmntq), got {cond_type}")
        self.visit(node.children[1])
        if len(node.children) == 3:
            self.visit(node.children[2])

    def visit_While(self, node: ASTNode):
        cond_type = self.visit(node.children[0])
        if cond_type != "d7kmntq":
            raise SemanticError(f"While condition must be bool (d7kmntq), got {cond_type}")
        self.visit(node.children[1])

    def visit_For(self, node: ASTNode):
        # init, cond, update, body
        self.symbols.push()
        self.visit(node.children[0])  # init
        cond_type = self.visit(node.children[1])
        if cond_type != "d7kmntq":
            raise SemanticError(f"For condition must be bool (d7kmntq), got {cond_type}")
        self.visit(node.children[2])  # update
        self.visit(node.children[3])  # body (Block)
        self.symbols.pop()

    def visit_Output(self, node: ASTNode):
        self.visit(node.children[0])  # any type

    def visit_Input(self, node: ASTNode):
        name = node.children[0].value
        self.symbols.lookup(name)  # must be declared

    def visit_Return(self, node: ASTNode):
        # main must not return a value
        if self.current_return_type is None:
            if node.children:
                raise SemanticError("Main function 'd7kbdaya' cannot return a value")
            return

        if not node.children:
            raise SemanticError(f"Function must return a value of type {self.current_return_type}")

        expr_type = self.visit(node.children[0])
        self._check_assign_compat(self.current_return_type, expr_type, "return statement")

    def visit_Call(self, node: ASTNode):
        fname = node.value
        ret_type, param_types = self.functions.lookup(fname)

        args = node.children
        if len(args) != len(param_types):
            raise SemanticError(
                f"Argument count mismatch in call to '{fname}': "
                f"expected {len(param_types)}, got {len(args)}"
            )

        for arg_node, expected in zip(args, param_types):
            t = self.visit(arg_node)
            self._check_assign_compat(expected, t, f"argument of '{fname}'")

        return ret_type

    def _check_assign_compat(self, var_type: str, expr_type: str, context: str):
        if var_type == expr_type:
            return
        # allow assigning int to decimal
        if var_type == "d7k34ry" and expr_type == "d7krqm":
            return
        raise SemanticError(f"Type mismatch in {context}: variable is {var_type}, expression is {expr_type}")


# =======================
# MAIN
# =======================

def main():
    tokens = scan_file("example.txt")

    print("=== TOKENS ===")
    for t in tokens:
        print(t)

    print("\n=== PARSING ===")
    parser = Parser(tokens)
    ast = parser.parse()
    pretty_print(ast)

    print("\n=== SEMANTIC ANALYSIS ===")
    analyzer = SemanticAnalyzer(ast)
    analyzer.analyze()
    print("Semantic analysis passed ✅")

if __name__ == "__main__":
    main()
