import time
import yaml

def measure_time(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    print(f"Tempo de execução: {end-start}")
    return result

def read_yaml(path: str)->dict:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return data

def print_stream(stream):
    for s in stream:
        message = s['messages'][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()