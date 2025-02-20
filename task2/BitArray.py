class BitArray:
    def __init__(self, in_bytes, bit_pointer):
        self.bytes = in_bytes
        self.bit_pointer = bit_pointer

    def __str__(self):
        output = ""
        for byte in self.bytes:
            output += format(byte, '08b') + " "
        return output[:-1-(8-self.bit_pointer)]
"""    
WILL BE CONTINUED IF NEEDED
def __add__(self, other):
        shifted = bytes([
            other[i]//self.bit_pointer + other[i+1]%self.bit_pointer for i in range(len(other)-1)
        ])
        total = self.bytes + shifted
        if not self.bit_pointer + other.bit_pointer % 8:
            total = total[:-1]
        return BitArray(total, self.bit_pointer + other.bit_pointer % 8)

    def __len__(self):
        return min(len(self.bytes*8 - 8 + self.bit_pointer), 0)

    def __and__(self, other):
        total_length = max(len(self), len(other))
"""