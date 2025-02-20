from BitArray import BitArray

def bitewise_string(bytes):
    output = ""
    for byte in bytes:
        output += format(byte, '08b') + " "
    return output

class BitSequenceFile:
    def __init__(self, file_path, write = False):
        self.unresolved_byte = 0 # value of unresolved byte
        self.bit_pointer = 0 # points to the unread/unwritten bit in unresolved byte
        self.byte_pointer = 0 # points to the position of the unresolved byte
        self.write = write
        try:
            if self.write:
                self.file = open(file_path, "wb")
            else:
                self.file = open(file_path, "rb")
        except:
            raise Exception("BitSequenceFile could not open file specified")

    def read(self, bits):
        if self.write:
            raise Exception("BitSequenceFile could not read file: file was opened for writing")
        self.file.seek(self.byte_pointer)
        useful_bytes = self.file.read((bits+self.bit_pointer)//8 + ((bits+self.bit_pointer)%8 > 0))
        self.byte_pointer += (bits+self.bit_pointer)//8
        if self.bit_pointer:
            useful_bytes = bytes([useful_bytes[0] & (2 ** self.bit_pointer - 1)]) + useful_bytes[1:]
            if (self.bit_pointer+bits) % 8 and bits > 7:
                useful_bytes = useful_bytes[:-1] + bytes([useful_bytes[-1] & (2 ** 8 - 2 ** (self.bit_pointer+bits) % 8)])
            if len(useful_bytes) > 1:
                useful_bytes = bytes([useful_bytes[i]<<self.bit_pointer + useful_bytes[i+1]>>(8-self.bit_pointer) for i in range(len(useful_bytes)-1)])
            else:
                useful_bytes = bytes([useful_bytes[0]<<self.bit_pointer])
        elif bits % 8:
            useful_bytes = useful_bytes[:-1] + bytes([useful_bytes[-1] & (2**8 - 2**(bits%8))])

        self.bit_pointer += bits%8
        self.bit_pointer %= 8
        return BitArray(useful_bytes, bits % 8)

    def close(self):
        try:
            self.file.close()
        except:
            raise Exception("BitSequenceFile failed to close file")