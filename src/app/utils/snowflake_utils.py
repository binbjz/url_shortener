import time
import threading


class SnowflakeIDGenerator:
    def __init__(self, data_center_id, worker_id):
        self.epoch = 1585644268888
        self.data_center_id_bits = 5
        self.worker_id_bits = 5
        self.sequence_bits = 12
        self.max_data_center_id = -1 ^ (-1 << self.data_center_id_bits)
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        self.worker_id_shift = self.sequence_bits
        self.data_center_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.data_center_id_bits

        if data_center_id > self.max_data_center_id or data_center_id < 0:
            raise ValueError("data_center_id超出范围")
        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError("worker_id超出范围")

        self.data_center_id = data_center_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _gen_timestamp(self):
        return int(time.time() * 1000)

    def _next_millis(self, last_timestamp: int):
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp

    def get_id(self):
        with self.lock:
            timestamp = self._gen_timestamp()
            if timestamp < self.last_timestamp:
                raise Exception("时钟回拨,无法生成ID")
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    timestamp = self._next_millis(self.last_timestamp)
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            new_id = ((timestamp - self.epoch) << self.timestamp_left_shift) | \
                     (self.data_center_id << self.data_center_id_shift) | \
                     (self.worker_id << self.worker_id_shift) | self.sequence
            return new_id


if __name__ == "__main__":
    id_generator = SnowflakeIDGenerator(data_center_id=0, worker_id=0)

    for _ in range(6):
        print(id_generator.get_id())
