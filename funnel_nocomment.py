import math, random, sys, hashlib

class FunnelHashTableSHA256:
    def __init__(self, capacity, delta=0.1, random_seed=None):
        self.random_gen = random.Random(random_seed)
        if capacity <= 0:
            raise ValueError("Capacity must be positive.")
        if not (0 < delta < 1):
            raise ValueError("delta must be between 0 and 1.")
        self.capacity = capacity
        self.delta = delta
        self.max_inserts = capacity - int(delta * capacity)
        self.num_inserts = 0
        self.probes = 0

        self.alpha = int(math.ceil(4 * math.log2(1 / delta) + 10))
        self.beta = int(math.ceil(2 * math.log2(1 / delta)))
        self.special_size = max(1, int(math.floor(3 * delta * capacity / 4)))
        self.primary_size = capacity - self.special_size
        self.special_size_b = self.special_size // 2
        self.special_size_c = self.special_size - self.special_size_b

        total_buckets = self.primary_size // self.beta
        a1 = (
            total_buckets / (4 * (1 - (0.75) ** self.alpha))
            if self.alpha > 0
            else total_buckets
        )
        self.levels = []
        self.level_bucket_counts = []
        self.level_salts = []
        self.level_bits = []
        remaining_buckets = total_buckets
        for i in range(self.alpha):
            a_i = max(1, int(round(a1 * (0.75) ** i)))
            if remaining_buckets <= 0 or a_i <= 0:
                break
            a_i = min(a_i, remaining_buckets)
            self.level_bucket_counts.append(a_i)
            level_size = a_i * self.beta
            level_array = [None] * level_size
            self.levels.append(level_array)
            self.level_salts.append(self.random_gen.randint(0, sys.maxsize))
            self.level_bits.append(max(1, math.ceil(math.log2(a_i))))
            remaining_buckets -= a_i
        if remaining_buckets > 0 and self.levels:
            extra = remaining_buckets * self.beta
            self.levels[-1].extend([None] * extra)
            self.level_bucket_counts[-1] += remaining_buckets
            remaining_buckets = 0

        self.special_array_b = [None] * self.special_size_b
        self.special_array_c = [None] * self.special_size_c
        self.salt_b = self.random_gen.randint(0, sys.maxsize)
        self.salt_c = self.random_gen.randint(0, sys.maxsize)
        self.bits_b = max(1, math.ceil(math.log2(self.special_size_b)))
        self.bucket_size_c = int(max(1, math.ceil(2 * math.log(math.log(self.capacity + 1) + 1))))
        self.num_buckets_c = self.special_size_c // self.bucket_size_c
        self.bits_c = max(1, math.ceil(math.log2(self.num_buckets_c)))

    def _get_candidate_indices(self, key, salt, bits_needed, upper_bound):
        h = hashlib.sha256(f"{key}-{salt}".encode()).digest()
        while True:
            bit_int = int.from_bytes(h, 'big')
            bitstring = bin(bit_int)[2:].zfill(256)
            bit_list = [int(b) for b in bitstring]
            for i in range(0, 256, bits_needed):
                if i + bits_needed <= 256:
                    chunk_bits = bit_list[i:i+bits_needed]
                    chunk_val = 0
                    for j, bit in enumerate(chunk_bits[::-1]):
                        chunk_val += bit * (2 ** j)
                    if chunk_val < upper_bound:
                        yield chunk_val
            h = hashlib.sha256(h).digest()

    def insert(self, key, value):
        self.probes = 0
        if self.num_inserts >= self.max_inserts:
            raise RuntimeError(
                "Hash table is full (maximum allowed insertions reached)."
            )
        for i in range(len(self.levels)):
            level = self.levels[i]
            num_buckets = self.level_bucket_counts[i]
            bits = self.level_bits[i]
            candidate_gen = self._get_candidate_indices(key, self.level_salts[i], bits, num_buckets)
            bucket_index = next(candidate_gen)
            start = bucket_index * self.beta
            end = start + self.beta
            for idx in range(start, end):
                self.probes += 1
                if level[idx] is None:
                    level[idx] = (key, value)
                    self.num_inserts += 1
                    return True
                elif level[idx][0] == key:
                    level[idx] = (key, value)
                    return True
        #inserimento in B
        gen = self._get_candidate_indices(key, self.salt_b, self.bits_b, self.special_size_b)
        probe_limit = int(max(1, math.ceil(math.log(math.log(self.capacity + 1) + 1))))
        for _ in range(probe_limit):
            idx = next(gen)
            self.probes += 1
            if self.special_array_b[idx] is None:
                self.special_array_b[idx] = (key, value)
                self.num_inserts += 1
                return True
            elif self.special_array_b[idx][0] == key:
                self.special_array_b[idx] = (key, value)
                return True
        #inserimento in C
        gen = self._get_candidate_indices(key, self.salt_c, self.bits_c, self.num_buckets_c)
        bucket_a_index = next(gen)
        bucket_b_index = next(gen)
        start_a = bucket_a_index * self.bucket_size_c
        start_b = bucket_b_index * self.bucket_size_c
        seq_a = list(range(start_a, start_a + self.bucket_size_c))
        seq_b = list(range(start_b, start_b + self.bucket_size_c))

        for i in range(self.bucket_size_c):
            for idx in (seq_a[i], seq_b[i]):
                self.probes += 1
                if self.special_array_c[idx] is None:
                    self.special_array_c[idx] = (key, value)
                    self.num_inserts += 1
                    return True
                elif self.special_array_c[idx][0] == key:
                    self.special_array_c[idx] = (key, value)
                    return True
        raise RuntimeError("Special array insertion failed; table is full.")

    def search(self, key):
        for i in range(len(self.levels)):
            level = self.levels[i]
            num_buckets = self.level_bucket_counts[i]
            bits = self.level_bits[i]
            for bucket_index in self._get_candidate_indices(key, self.level_salts[i], bits, num_buckets):
                start = bucket_index * self.beta
                end = start + self.beta
                for idx in range(start, end):
                    if level[idx] is None:
                        break
                    elif level[idx][0] == key:
                        return level[idx][1]

        gen_b = self._get_candidate_indices(key, self.salt_b, self.bits_b, self.special_size_b)
        probe_limit = int(max(1, math.ceil(math.log(math.log(self.capacity + 1) + 1))))
        for _ in range(probe_limit):
            idx = next(gen_b)
            if self.special_array_b[idx] is None:
                break
            elif self.special_array_b[idx][0] == key:
                return self.special_array_b[idx][1]

        gen_c = self._get_candidate_indices(key, self.salt_c, self.bits_c, self.num_buckets_c)
        bucket_a_index = next(gen_c)
        bucket_b_index = next(gen_c)
        start_a = bucket_a_index * self.bucket_size_c
        start_b = bucket_b_index * self.bucket_size_c
        seq_a = list(range(start_a, start_a + self.bucket_size_c))
        seq_b = list(range(start_b, start_b + self.bucket_size_c))

        for i in range(self.bucket_size_c):
            for idx in (seq_a[i], seq_b[i]):
                if self.special_array_c[idx] and self.special_array_c[idx][0] == key:
                    return self.special_array_c[idx][1]
        return None

def __setitem__(self, key, value):
    self.insert(key, value)

def __contains__(self, key):
    return self.search(key) is not None

def __len__(self):
    return self.num_inserts

def __getitem__(self, key):
    ret = self.search(key)
    if ret is None:
        raise KeyError(key)
    return ret

def get(self, key, default=None):
    return self.search(key) or default
