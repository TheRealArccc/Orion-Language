import time
from lexer import Lexer
from parser import Parser

start_time = time.perf_counter()

def main():
    file_path = r'C:\Users\ryann_xf04h2j\OneDrive\Documents\other scripts\PROJECTS\InterTestBuild\v3\script.txt'
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            
        lexer = Lexer(content)
        tokens = list(lexer.generate_tokens())
        print(tokens)
        parser = Parser(tokens)
        tree = parser.parse()
        print(tree)
    except FileNotFoundError:
        raise 'file does not exist'

if __name__ == '__main__':
    main()

end_time = time.perf_counter()
print(f"Executed in {(end_time-start_time)*1000:.4f}ms")