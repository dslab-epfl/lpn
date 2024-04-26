import inspect

def example_function():
    return "Inspect me!"

try:
    source_code = inspect.getsource(example_function)
    print(source_code)
except (TypeError, OSError) as error:
    print(f"Could not get source code: {error}")

