from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict, Union


class DataStream(ABC):
    def __init__(self, stream_id: str, stream_type: str):
        self.stream_id = stream_id
        self.stream_type = stream_type
        self.processed_count = 0

    @abstractmethod
    def process_batch(self, data_batch: List[Any]) -> str:
        pass

    def filter_data(self, data_batch: List[Any],
                    criteria: Optional[str] = None) -> List[Any]:
        if not criteria:
            return data_batch
        return [item for item in data_batch if criteria in str(item).lower()]

    def get_stats(self) -> Dict[str, Union[str, int, float]]:
        return {
            "ID": self.stream_id,
            "Type": self.stream_type,
            "Processed": self.processed_count
        }


class SensorStream(DataStream):
    def __init__(self, stream_id: str):
        super().__init__(stream_id, "Environmental Data")
        self.total_temp = 0.0

    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            readings = [float(val) for val in data_batch
                        if isinstance(val, (int, float))]
            self.processed_count += len(readings)
            self.total_temp += sum(readings)
            avg = sum(readings) / len(readings) if readings else 0
            return f"Sensor analysis: {len(readings)} readings processed, avg: {avg:.1f}°C"
        except (ValueError, ZeroDivisionError) as e:
            return f"Error in SensorStream: {e}"


class TransactionStream(DataStream):
    def __init__(self, stream_id: str):
        super().__init__(stream_id, "Financial Data")
        self.net_flow = 0.0

    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            current_batch_flow = 0.0
            for item in data_batch:
                if isinstance(item, str) and ":" in item:
                    action, val = item.split(":")
                    amount = float(val)
                    current_batch_flow += amount if action == "buy" \
                        else -amount

            self.net_flow += current_batch_flow
            self.processed_count += len(data_batch)
            prefix = "+" if current_batch_flow >= 0 else ""
            return f"Transaction analysis: {len(data_batch)} operations, net flow: {prefix}{current_batch_flow} units"
        except Exception as e:
            return f"Transaction error: {e}"


class EventStream(DataStream):
    def __init__(self, stream_id: str):
        super().__init__(stream_id, "System Events")
        self.errors = 0

    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            batch_errors = len([e for e in data_batch
                                if "error" in str(e).lower()])
            self.errors += batch_errors
            self.processed_count += len(data_batch)
            return f"Event analysis: {len(data_batch)} events, {batch_errors} error(s) detected"
        except Exception as e:
            return f"Event error: {e}"


class StreamProcessor:

    def __init__(self):
        self.streams: List[DataStream] = []

    def add_stream(self, stream: DataStream):
        if isinstance(stream, DataStream):
            self.streams.append(stream)

    def process_all(self, data_map: Dict[str, List[Any]]):
        print("=== Polymorphic Stream Processing ===")
        print("Processing mixed stream types through unified interface...\n")

        for stream in self.streams:
            batch = data_map.get(stream.stream_id, [])
            try:
                result = stream.process_batch(batch)
                print(f"- {stream.stream_id}: {result}")
            except Exception as e:
                print(f"Failed to process stream {stream.stream_id}: {e}")


if __name__ == "__main__":
    print("=== CODE NEXUS - POLYMORPHIC STREAM SYSTEM ===")

    s1 = SensorStream("SENSOR_001")
    print(f"\nInitializing Sensor Stream...\n"
          f"Stream ID: {s1.stream_id}, Type: {s1.stream_type}")
    print(s1.process_batch([22.5, 23.0, 22.0]))

    t1 = TransactionStream("TRANS_001")
    print(f"\nInitializing Transaction Stream...\nStream ID:"
          f"{t1.stream_id}, Type: {t1.stream_type}")
    print(t1.process_batch(["buy:100", "sell:150", "buy:75"]))

    e1 = EventStream("EVENT_001")
    print(f"\nInitializing Event Stream...\nStream ID: {e1.stream_id},"
          f" Type: {e1.stream_type}")
    print(e1.process_batch(["login", "error", "logout"]))

    processor = StreamProcessor()
    processor.add_stream(s1)
    processor.add_stream(t1)
    processor.add_stream(e1)

    mixed_data = {
        "SENSOR_001": [25.0, 26.5],
        "TRANS_001": ["buy:500", "sell:200", "buy:100", "sell:50"],
        "EVENT_001": ["critical_error", "disk_full", "login"]
    }

    print("\n")
    processor.process_all(mixed_data)

    print("\nStream filtering active: High-priority data only")
    critical_events = e1.filter_data(mixed_data["EVENT_001"], criteria="error")
    print(f"Filtered results: {len(critical_events)} critical sensor alerts")

    print("All streams processed successfully. Nexus throughput optimal.")
