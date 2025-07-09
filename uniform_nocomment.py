import hashlib, math

class UniformHashingSHA256:
    def __init__(self, capacity, delta=0.1, random_seed=None): 
        if capacity <= 0: 
            raise ValueError("Capacity must be a positive number.")
        if delta <= 0 or delta >= 1:
            raise ValueError("Delta must be in the range (0, 1).")
        self.capacity = capacity
        self.delta = delta
        self.max_inserts = capacity - int(delta * capacity)
        self.num_inserts = 0
        self.table = [None] * capacity
        self.probes = 0
        self.total_probes = 0
        self.bits_needed = math.ceil(math.log2(capacity))  

    def _get_candidate_indices(self, key):
        h = hashlib.sha256(str(key).encode()).digest()
        bits_needed = self.bits_needed

        while True:
            bit_int = int.from_bytes(h, 'big')
            bitstring = bin(bit_int)[2:].zfill(256)
            bit_list = [int(b) for b in bitstring]

            for i in range(0, 256, bits_needed): 
                if i + bits_needed <= 256:
                    chunk_bits = bit_list[i:i+bits_needed]
                    chunk_val = 0
                    for j, bit in enumerate(chunk_bits[::-1]):
                        chunk_val += bit * (2**j)
                    if chunk_val < self.capacity:
                        yield chunk_val
            h = hashlib.sha256(h).digest()

    def insert(self, key, value):
        self.probes = 0
        if self.num_inserts >= self.max_inserts:
            raise OverflowError("Maximum number of inserts reached, hash table is full.")

        for index in self._get_candidate_indices(key):
            self.probes += 1
            self.total_probes += 1
            if self.table[index] is None:
                self.table[index] = (key, value)
                self.num_inserts += 1
                return True
            elif self.table[index][0] == key:
                self.table[index] = (key, value)
                return True

    def search(self, key):
        for index in self._get_candidate_indices(key):
            if self.table[index] is None:
                return None
            if self.table[index][0] == key:
                return self.table[index][1]

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __getitem__(self, key):
        result = self.search(key)
        if result is None:
            raise KeyError(f"Key {key} not found.")
        return result

    def get(self, key, default=None):
        return self.search(key) or default

    def __contains__(self, key):
        return self.search(key) is not None

    def __len__(self):
        return self.num_inserts
