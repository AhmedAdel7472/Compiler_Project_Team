import re
import sys


TOKENS = {
    "KEYWORD": [
         "d7ktba3a", "d7ked5al", "d7klo", "d7k8er",
        "d7kdw5ny", "d7klf",
    ],
    "DATA_TYPE": [
        "d7krkm", "d7k34ry", "d7kmslsl", "d7kmntk", "d7khrf", "d7krg3"
    ],
    ""
    "SYMBOL": [r"\{", r"\}", r"\(", r"\)", r";", r"\[", r"\]"],
    "OPERATORS": [r"\+", r"\-", r"\*", r"\\",],
    "COMMENT": [r"//.*", r"/\*[\s\S]*?\*/"],
    "STRING": [r"\".*?\"", r"‘.*?’", r"“.*?”"]
}

TOKEN_TYPES = {
    # Control flow
    "d7klo": "IF_STATEMENT",
    "d7k8er": "ELSE_BLOCK",
    "d7kdw5ny": "WHILE_LOOP",
    "d7klf": "FOR_LOOP",
    "d7krg3": "RETURN_STATEMENT",
    # Structure & I/O
    "d7ktba3a": "OUTPUT",
    "d7ked5al": "INPUT",
    "d7kkml": "CONTINUE",
    # Data types
    "d7krkm": "INTEGER_TYPE",
    "d7k34ry": "DOUBLE_TYPE",
    "d7kmslsl": "STRING_TYPE",
    "d7kmntk": "BOOLEAN_TYPE",
    "d7khrf": "CHAR_TYPE"
    # Comments
}




# Return tokens in the required formate for parser
def scanner():
    results = []
    
    def scan_line(line):
        results = []
        for token_type, patterns in TOKENS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    lexeme = match.group()
                    results.append((token_type, lexeme))
        return results
    
    # Read file
    filename = "example.txt"
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
    for i, line in enumerate(lines, start=1):
        tokens = scan_line(line)
        for token_type, lexeme in tokens:
            results.append((token_type, lexeme))

    return results
def main():
    print(scanner())
    
    
main()