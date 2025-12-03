import time
from lexer import Lexer
from parser import Parser
from runtime.interpreter import Interpreter

current_ver = "0.1.0"
start_time = time.perf_counter()

def run_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            
        lexer = Lexer(content)
        tokens = list(lexer.generate_tokens())
        # print(tokens)
        parser = Parser(tokens)
        tree = parser.parse()
        # print(tree)

        interpreter = Interpreter()
        interpreter.interpret(tree)
        # print(interpreter.env.scopes)
    except FileNotFoundError:
        raise 'file does not exist'

if __name__ == '__main__':
    pass

end_time = time.perf_counter()
# print(f"Executed in {(end_time-start_time)*1000:.4f}ms")