import sys
from main import run_file

def main():
    if len(sys.argv) == 2:
        run_file(sys.argv[1])
        sys.exit(1)
    else:
        print("Usage: orion <script.or>")
        sys.exit(1)

main()
