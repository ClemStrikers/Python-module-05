from abc import ABC, abstractmethod
from typing import Any, List


class DataProcessor(ABC):
    def __init__(self) -> None:
        self._storage: List[tuple[int, str]] = []
        self._counter: int = 0
        self.total_processed: int = 0

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
        if isinstance(data, list) and data:
            return all(isinstance(i, (int, float)) for i in data)
        return False

    def ingest(self, data: Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")
        items = data if isinstance(data, list) else [data]
        for item in items:
            self._storage.append((self._counter, str(item)))
            self._counter += 1
            self.total_processed += 1


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        if isinstance(data, list) and data:
            return all(isinstance(i, str) for i in data)
        return False

    def ingest(self, data: Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")
        items = data if isinstance(data, list) else [data]
        for item in items:
            self._storage.append((self._counter, item))
            self._counter += 1
            self.total_processed += 1


class LogProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        if isinstance(data, dict):
            return all(isinstance(k, str) and
                       isinstance(v, str) for k, v in data.items())
        if isinstance(data, list) and data:
            return all(self.validate(i) for i in data if isinstance(i, dict))
        return False

    def ingest(self, data: Any) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")
        items = data if isinstance(data, list) else [data]
        for item in items:
            log_str = ": ".join(item.values())
            self._storage.append((self._counter, log_str))
            self._counter += 1
            self.total_processed += 1


class DataStream:
    def __init__(self) -> None:
        self._processors: List[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        self._processors.append(proc)

    def process_stream(self, stream: List[Any]) -> None:
        for element in stream:
            handled = False
            for proc in self._processors:
                if proc.validate(element):
                    proc.ingest(element)
                    handled = True
                    break
            if not handled:
                print(f"DataStream error-"
                      f"Can't process element in stream: {element}")

    def print_processors_stats(self) -> None:
        print("== DataStream statistics ==")
        if not self._processors:
            print("No processor found, no data")
            return
        for proc in self._processors:
            name = proc.__class__.__name__.replace("Processor", " Processor")
            total = proc.total_processed
            rem = len(proc._storage)
            print(f"{name}: total {total} items processed,"
                  f"remaining {rem} on processor")


def main() -> None:
    print("=== Code Nexus- Data Stream ===")
    print("Initialize Data Stream...")
    ds = DataStream()
    ds.print_processors_stats()

    print("Registering Numeric Processor")
    num_p = NumericProcessor()
    ds.register_processor(num_p)

    batch = [
        'Hello world',
        [3.14, -1, 2.71],
        [
            {'log_level': 'WARNING', 'log_message':
             'Telnet access! Use ssh instead'},
            {'log_level': 'INFO', 'log_message': 'User wil is connected'}
        ],
        42,
        ['Hi', 'five']
    ]

    print("Send first batch of data on stream: " + str(batch))
    ds.process_stream(batch)
    ds.print_processors_stats()

    print("Registering other data processors")
    txt_p = TextProcessor()
    log_p = LogProcessor()
    ds.register_processor(txt_p)
    ds.register_processor(log_p)

    print("Send the same batch again")
    ds.process_stream(batch)
    ds.print_processors_stats()

    print("Consume some elements from the data processors:"
          "Numeric 3, Text 2, Log 1")
    for _ in range(3):
        num_p.output()
    for _ in range(2):
        txt_p.output()
    for _ in range(1):
        log_p.output()

    ds.print_processors_stats()


if __name__ == "__main__":
    main()
