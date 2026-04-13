from abc import ABC, abstractmethod
from typing import Any, Union


class DataProcessor(ABC):
    def __init__(self) -> None:
        self._storage: list[tuple[int, str]] = []
        self._counter: int = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        if not self._storage:
            raise IndexError("No data to output")
        return self._storage.pop(0)


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, (int, float)):
            return True
        if isinstance(data, list):
            return all(isinstance(i, (int, float)) for i in data)
        return False

    def ingest(self, data: Union[int, float, list[Union[int, float]]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")

        items = data if isinstance(data, list) else [data]
        for item in items:
            self._storage.append((self._counter, str(item)))
            self._counter += 1


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        if isinstance(data, list):
            return all(isinstance(i, str) for i in data)
        return False

    def ingest(self, data: Union[str, list[str]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")

        items = data if isinstance(data, list) else [data]
        for item in items:
            self._storage.append((self._counter, item))
            self._counter += 1


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, dict):
            return all(isinstance(k, str) and isinstance(v, str)
                       for k, v in data.items())
        if isinstance(data, list):
            return all(self.validate(i) for i in data if isinstance(i, dict))
        return False

    def ingest(self, data: Union[dict[str, str],
                                 list[dict[str, str]]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")

        items = data if isinstance(data, list) else [data]
        for item in items:
            log_str = ": ".join(item.values())
            self._storage.append((self._counter, log_str))
            self._counter += 1


def main() -> None:
    print("=== Code Nexus- Data Processor ===")

    print("Testing Numeric Processor...")
    num_p = NumericProcessor()
    print(f"Trying to validate input '42': {num_p.validate(42)}")
    print(f"Trying to validate input 'Hello': {num_p.validate('Hello')}")
    print("Test invalid ingestion of string 'foo' without prior validation:")
    try:
        num_p.ingest("foo")  # type: ignore
    except Exception as e:
        print(f"Got exception: {e}")

    num_p.ingest([1, 2, 3, 4, 5])
    print("Processing data: [1, 2, 3, 4, 5]")
    print("Extracting 3 values...")
    for _ in range(3):
        rank, val = num_p.output()
        print(f"Numeric value {rank}: {val}")

    print("Testing Text Processor...")
    txt_p = TextProcessor()
    print(f"Trying to validate input '42': {txt_p.validate(42)}")
    txt_p.ingest(["Hello", "Nexus", "World"])
    print("Processing data: ['Hello', 'Nexus', 'World']")
    print("Extracting 1 value...")
    rank, val = txt_p.output()
    print(f"Text value {rank}: {val}")

    print("Testing Log Processor...")
    log_p = LogProcessor()
    print(f"Trying to validate input 'Hello': {log_p.validate('Hello')}")
    logs = [
        {"level": "NOTICE", "msg": "Connection to server"},
        {"level": "ERROR", "msg": "Unauthorized access!!"}
    ]
    log_p.ingest(logs)
    print(f"Processing data: {logs}")
    print("Extracting 2 values...")
    for _ in range(2):
        rank, val = log_p.output()
        print(f"Log entry {rank}: {val}")


if __name__ == "__main__":
    main()
