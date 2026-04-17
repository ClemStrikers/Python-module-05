from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Protocol


class ExportPlugin(Protocol):
    def process_output(self, data: List[Tuple[int, str]]) -> None:
        ...


class DataProcessor(ABC):
    def __init__(self) -> None:
        self._storage: List[Tuple[int, str]] = []
        self._counter: int = 0
        self.total_processed: int = 0

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> Tuple[int, str]:
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
            return all(isinstance(k, str)
                       and isinstance(v, str) for k, v in data.items())
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


class CSVExport:
    def process_output(self, data: List[Tuple[int, str]]) -> None:
        print("CSV Output:")
        print(",".join([val for _, val in data]))


class JSONExport:
    def process_output(self, data: List[Tuple[int, str]]) -> None:
        print("JSON Output:")
        items: List[str] = []
        for rank, val in data:
            items.append(f'"item_{rank}": "{val}"')
        print("{" + ", ".join(items) + "}")


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
        print("\n== DataStream statistics ==")
        if not self._processors:
            print("No processor found, no data")
            return
        for proc in self._processors:
            name = proc.__class__.__name__.replace("Processor", " Processor")
            total = proc.total_processed
            rem = len(proc._storage)
            print(f"{name}: total {total} items processed,"
                  f"remaining {rem} on processor")

    def output_pipeline(self, nb: int, plugin: ExportPlugin) -> None:
        for proc in self._processors:
            extracted: List[Tuple[int, str]] = []
            for _ in range(nb):
                try:
                    extracted.append(proc.output())
                except IndexError:
                    break
            if extracted:
                plugin.process_output(extracted)


def main() -> None:
    print("=== Code Nexus- Data Pipeline ===")
    print("\nInitialize Data Stream...")
    ds = DataStream()
    ds.print_processors_stats()

    print("\nRegistering Processors")
    ds.register_processor(NumericProcessor())
    ds.register_processor(TextProcessor())
    ds.register_processor(LogProcessor())

    batch1 = [
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

    print(f"\nSend first batch of data on stream: {batch1}")
    ds.process_stream(batch1)
    ds.print_processors_stats()

    print("\nSend 3 processed data from each processor to a CSV plugin:")
    csv_plugin = CSVExport()
    ds.output_pipeline(3, csv_plugin)
    ds.print_processors_stats()

    batch2 = [
        21,
        ['I love AI', 'LLMs are wonderful', 'Stay healthy'],
        [
            {'log_level': 'ERROR', 'log_message': '500 server crash'},
            {'log_level': 'NOTICE', 'log_message':
             'Certificate expires in 10 days'}
        ],
        [32, 42, 64, 84, 128, 168],
        'World hello'
    ]

    print(f"\nSend another batch of data: {batch2}")
    ds.process_stream(batch2)
    ds.print_processors_stats()

    print("\nSend 5 processed data from each processor to a JSON plugin:")
    json_plugin = JSONExport()
    ds.output_pipeline(5, json_plugin)
    ds.print_processors_stats()


if __name__ == "__main__":
    main()
