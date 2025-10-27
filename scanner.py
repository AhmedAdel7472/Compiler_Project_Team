import re

# ==========================
# 🏀 BallScript Token Definitions (Updated)
# ==========================

TOKENS = {
    "KEYWORD": [
        "d7kdlal", "d7ktba3a", "d7ked5al", "d7klo", "d7k8er",
        "d7kdw5ny", "d7klf", "d7krg3", "#d7khaaat", "d7kspaace"
        ,"main"
    ],
    "DATA_TYPE": [
        "d7krkm", "d7k34ry", "d7kmslsl", "d7kmntk", "d7khrf"
    ],
    "SYMBOL": [r"\{", r"\}", r"\(", r"\)", r";", r"\[", r"\]", r"\+\+", r"--"],
    "COMMENT": [r"//.*",r"/\*[\s\S]*?\*/"],
    "STRING": [r"\".?\"", r"‘.?’", r"“.*?”"]
}

# ==========================
# 🏁 Sub-Type Mapping for Output
# ==========================

TOKEN_TYPES = {
    # Control flow
    "d7klo": "IF_STATEMENT",
    "d7k8er": "ELSE_BLOCK",
    "d7kdw5ny": "WHILE_LOOP",
    "d7klf": "FOR_LOOP",
    "d7krg3": "RETURN_STATEMENT",

    # Structure & I/O
    "d7kdlal": "FUNCTION_DEF",
    "d7ktba3a": "OUTPUT",      # updated from d7ktl3
    "d7ked5al": "INPUT",       # updated from d7kd5l
    "d7kkml": "UNKNOWN",       # added placeholder for d7k5d
    "#d7khaaat": "IMPORT_LIB",
    "d7kspaace": "NAMESPACE",
    "main" : "Main_function",

    # Data types
    "d7krkm": "INTEGER_TYPE",
    "d7k34ry": "DOUBLE_TYPE",
    "d7kmslsl": "STRING_TYPE",
    "d7kmntk": "BOOLEAN_TYPE",
    "d7khrf": "CHAR_TYPE"
}


# ==========================
# 🧠 Scanner Function
# ==========================

def scan_line(line_num, line):
    results = []
    for token_type, patterns in TOKENS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                value = match.group()
                subtype = TOKEN_TYPES.get(value, "")
                results.append((token_type, subtype, value))
    return results


# ==========================
# 🏀 Main Function
# ==========================

def main():
    filename = "example.txt"  # BallScript source file
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for i, line in enumerate(lines, start=1):
        tokens = scan_line(i, line)
        for token_type, subtype, value in tokens:
            print(f"[Line {i}] {token_type:<10} | {subtype:<18} {value}")

if __name__ == "__main__":
    main()
# ==========================
# 🏁 End of BallScript Token Scanner