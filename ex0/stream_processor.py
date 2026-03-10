from abc import ABC, abstractmethod
from typing import Any, List, Union


class DataProcessor(ABC):
    @abstractmethod
    def process(self, data: Any) -> str:
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    def format_output(self, result: str) -> str:
        return f"Output: {result}"


class NumericProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return isinstance(data, list) and\
            all(isinstance(x, (int, float)) for x in data)

    def process(self, data: List[Union[int, float]]) -> str:
        total = sum(data)
        avg = total / len(data) if data else 0
        return self.format_output(f"Processed {len(data)} numeric values,"
                                  f"sum ={total}, avg = {avg}")


class TextProcessor(DataProcessor):
    def validate(self, data: Any) -> bool:
        return isinstance(data, str)

    def process(self, data: str) -> str:
        words = len(data.split())
        return self.format_output(f"Processed text: {len(data)} characters,"
                                  f"{words} words")
