from pathlib import Path


def greet(name: str = "world") -> str:
    message = f"hello, {name}"
    full_path = Path(__file__).parent / "data" / "x.json"
    print(f"Full path to x.json: {full_path}")
    return message


if __name__ == "__main__":
    greeting = greet("23")
