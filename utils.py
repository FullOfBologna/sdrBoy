import inspect

def print_function():
    caller_frame = inspect.currentframe().f_back
    function_name = caller_frame.f_code.co_name
    print(f'\n{function_name}\n')