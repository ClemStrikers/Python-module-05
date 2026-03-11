from abc import ABC, abstractmethod
from typing import Any, List, Union


class DataProcessor(ABC):

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def process(self, data: Any) -> str:
        pass

    def format_output(self, result: str) -> str:
        return f"Output: {result}"


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return isinstance(data, list) and all(isinstance(x, (int, float))
                                              for x in data)

    def process(self, data: List[Union[int, float]]) -> str:
        total = sum(data)
        avg = total / len(data) if data else 0.0
        res_str = f"Processed {len(data)} numeric values,"
        f"sum={total}, avg={avg}"
        return super().format_output(res_str)


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return isinstance(data, str)

    def process(self, data: str) -> str:
        words = len(data.split())
        res_str = f"Processed text: {len(data)} characters, {words} words"
        return super().format_output(res_str)


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return isinstance(data, str) and ":" in data

    def format_output(self, result: str) -> str:
        return result

    def process(self, data: str) -> str:
        parts = data.split(":", 1)
        level = parts[0].strip()
        message = parts[1].strip()
        tag = "[ALERT]" if "ERROR" in level else "[INFO]"
        res_str = f"{tag} {level} level detected: {message}"
        return self.format_output(res_str)


def run_system():
    print("=== CODE NEXUS - DATA PROCESSOR FOUNDATION ===")

    processors = {
        "Numeric": (NumericProcessor(), [1, 2, 3, 4, 5]),
        "Text": (TextProcessor(), "Hello Nexus World"),
        "Log": (LogProcessor(), "ERROR: Connection timeout")
    }

    for name, (proc, data) in processors.items():
        print(f"Initializing {name} Processor...")
        try:
            if proc.validate(data):
                print(f"Processing data: {data}")
                print(f"Validation: {name} data verified")
                print(proc.process(data))
        except Exception as e:
            print(f"Error: {e}")

    print("\n=== Polymorphic Processing Demo ===")
    print("Processing multiple data types through same interface...")

    demo_list = [
        (NumericProcessor(), [1, 2, 3]),
        (TextProcessor(), "Hello Nexus"),
        (LogProcessor(), "INFO: System ready")
    ]

    for i, (p, d) in enumerate(demo_list, 1):
        print(f"Result {i}: {p.process(d)}")

    print("\nFoundation systems online. Nexus ready for advanced streams.")


if __name__ == "__main__":
    run_system()
