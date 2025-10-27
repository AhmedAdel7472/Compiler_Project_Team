import re

# -----------------------------
# Token Definitions
# -----------------------------
TOKENS = {
    "KEYWORD": [
        "d7kdlal", "d7ktba3a", "d7ked5al", "d7klo", "d7k8er",
        "d7kdw5ny", "d7klf", "d7krg3", "#d7khaaat", "d7kspaace",
        "main"
    ],
    "DATA_TYPE": [
        "d7krkm", "d7k34ry", "d7kmslsl", "d7kmntk", "d7khrf"
    ],
    "SYMBOL": [r"\{", r"\}", r"\(", r"\)", r";", r"\[", r"\]", r"\+\+", r"--"],
    "COMMENT": [r"//.*", r"/\*[\s\S]*?\*/"],
    "STRING": [r"\".*?\"", r"‘.*?’", r"“.*?”"]
}

# Mapping BallScript keywords to C++-like meaning
TOKEN_TYPES = {
    # Control flow
    "d7klo": "IF_STATEMENT",
    "d7k8er": "ELSE_BLOCK",
    "d7kdw5ny": "WHILE_LOOP",
    "d7klf": "FOR_LOOP",
    "d7krg3": "RETURN_STATEMENT",

    # Structure & I/O
    "d7kdlal": "FUNCTION_DEF",
    "d7ktba3a": "OUTPUT",
    "d7ked5al": "INPUT",
    "d7kkml": "UNKNOWN",
    "#d7khaaat": "IMPORT_LIB",
    "d7kspaace": "NAMESPACE",
    "main": "MAIN_FUNCTION",

    # Data types
    "d7krkm": "INTEGER_TYPE",
    "d7k34ry": "DOUBLE_TYPE",
    "d7kmslsl": "STRING_TYPE",
    "d7kmntk": "BOOLEAN_TYPE",
    "d7khrf": "CHAR_TYPE"
}


# -----------------------------
# Token Class
# -----------------------------
class Token:
    def __init__(self, category, lexeme, subtype=None, line_number=None):
        self.category = category      # e.g., KEYWORD, SYMBOL, DATA_TYPE
        self.lexeme = lexeme          # actual text from source (e.g., d7klo)
        self.subtype = subtype or ""  # deeper meaning (e.g., IF_STATEMENT)
        self.line_number = line_number

    def __str__(self):
        return f"[Line {self.line_number}] {self.category:<15} | {self.subtype:<20} {self.lexeme}"


# -----------------------------
# Scanner Class
# -----------------------------
class D7KScriptScanner:
    def __init__(self, tokens_map, token_types):
        self.tokens_map = tokens_map
        self.token_types = token_types

    def scan_line(self, line, line_number):
        results = []
        for category, patterns in self.tokens_map.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    lexeme = match.group()
                    subtype = self.token_types.get(lexeme, "")
                    token = Token(category, lexeme, subtype, line_number)
                    results.append(token)
        return results

    def scan_file(self, filename):
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        all_tokens = []
        for i, line in enumerate(lines, start=1):
            tokens = self.scan_line(line, i)
            all_tokens.extend(tokens)
        return all_tokens


# -----------------------------
# Main Entry Point
# -----------------------------
def main():
    scanner = BallScriptScanner(TOKENS, TOKEN_TYPES)
    filename = "example.txt"

    tokens = scanner.scan_file(filename)

    print("=== BallScript Token Scanner ===\n")
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
