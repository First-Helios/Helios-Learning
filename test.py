from pathlib import Path


def greet(name: str = "world"):
    message = f"hello, {name}"
    full_path = Path(__file__).parent / "data" / "x.json"
    print(f"Full path to x.json: {full_path}")
    return message
