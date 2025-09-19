import sys, re, pathlib

def has_comments(py_text: str) -> bool:
    # crude but effective for our tests canon: no line starting with '#' (ignoring whitespace)
    # and no triple-quoted docstrings (""" or ''')
    if re.search(r'^\s*#', py_text, flags=re.M):
        return True
    if re.search(r'("""|\'\'\')', py_text):
        return True
    return False

def main():
    if len(sys.argv) != 2:
        print("usage: python tools/no_comments_check.py path/to/solution_test.py")
        sys.exit(2)
    path = pathlib.Path(sys.argv[1])
    if not path.exists():
        print("file not found")
        sys.exit(2)
    text = path.read_text(encoding="utf-8", errors="ignore")
    bad = has_comments(text)
    print("HAS_COMMENTS" if bad else "OK")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
