from xml.sax.saxutils import escape

from BitArray import BitArray

def bytewise_string(bytes):
    output = ""
    for byte in bytes:
        output += format(byte, '08b') + " "
    return output

class BitSequenceFile:
    def __init__(self, file_path, write_mode = -1):
        self.unresolved_byte = 0 # value of unresolved byte
        self.bit_pointer = 0 # points to the unread/unwritten bit in unresolved byte
        self.byte_pointer = 0 # points to the position of the unresolved byte
        self.write_mode = write_mode
        if self.write_mode > -1:
            self.opened_byte = 0
        try:
            if self.write_mode > -1:

                if self.write_mode:
                    self.file = open(file_path, "ab")
                    self.file.seek(0 ,2)
                    self.byte_pointer = self.file.tell()
                else:
                    self.file = open(file_path, "wb")
            else:
                self.file = open(file_path, "rb")
        except:
            raise Exception("BitSequenceFile could not open file specified")

    def read(self, bits):
        force_debug = False
        if force_debug: print("Reading. byte", self.byte_pointer, "bit", self.bit_pointer, "len", bits)
        if self.write_mode != -1:
            raise Exception("BitSequenceFile could not read file: file was opened for writing")
        self.file.seek(self.byte_pointer)
        raw_bytes = self.file.read((bits+self.bit_pointer)//8 + ((bits+self.bit_pointer)%8 > 0))
        if force_debug: print("raw bytes", bytewise_string(raw_bytes))
        self.byte_pointer += (bits+self.bit_pointer)//8
        useful_bytes = bytes([])
        if self.bit_pointer:
            useful_bytes += bytes([raw_bytes[0] & (2 ** 8 - 2**self.bit_pointer)])
            if force_debug: print("first useful", bytewise_string(useful_bytes))
            if len(raw_bytes) > 2:
                useful_bytes += raw_bytes[1:-1]
                if force_debug: print("middle useful", bytewise_string(useful_bytes))
            if len(raw_bytes) > 1:
                if (self.bit_pointer + bits) % 8:
                    useful_bytes += bytes([raw_bytes[-1]  & (2 ** ((self.bit_pointer + bits) % 8) -1)])
                else:
                    useful_bytes += bytes([raw_bytes[-1]])
                if force_debug: print("trailing useful", bytewise_string(useful_bytes))
            if len(useful_bytes) > 1:
                shifted_bytes_a = bytes([
                    useful_bytes[i]>>self.bit_pointer
                    for i in range(len(useful_bytes)-1)])
                shifted_bytes_b = bytes([
                    (useful_bytes[i+1]<<(8-self.bit_pointer))&(2**8-1)
                    for i in range(len(useful_bytes)-1)])
                shifted_bytes = bytes([shifted_bytes_a[i] + shifted_bytes_b[i] for i in range(len(shifted_bytes_a))])
                if force_debug: print("a", bytewise_string(shifted_bytes_a))
                if force_debug: print("b", bytewise_string(shifted_bytes_b))
                if force_debug: print("shifted useful", bytewise_string(shifted_bytes))

                if (bits + self.bit_pointer) % 8 > self.bit_pointer:
                    shifted_bytes += bytes([useful_bytes[-1] >> self.bit_pointer])
                    if force_debug: print("trailing shifted useful", bytewise_string(shifted_bytes))
                useful_bytes = shifted_bytes
            else:
                useful_bytes = bytes([useful_bytes[0]>>self.bit_pointer])
                if force_debug: print("short shifted useful", bytewise_string(useful_bytes))
        elif bits % 8:
            if bits > 8:
                useful_bytes = raw_bytes[:-1] + bytes([raw_bytes[-1] & (2 ** ((self.bit_pointer+bits) % 8) -1)])
                if force_debug: print("unshifted useful", bytewise_string(useful_bytes))
            else:
                useful_bytes = bytes([raw_bytes[-1] & (2 ** ((self.bit_pointer + bits) % 8) - 1)])
                if force_debug: print("short unshifted useful", bytewise_string(useful_bytes))
        else:
            if force_debug: print("direct useful", bytewise_string(useful_bytes))
            useful_bytes = raw_bytes
        self.bit_pointer += bits%8
        self.bit_pointer %= 8
        useful_pointer = bits % 8
        if useful_pointer == 0:
            useful_pointer = 8
        if force_debug: print(bytewise_string(useful_bytes), useful_pointer)
        return BitArray(useful_bytes, useful_pointer)

    def write(self, bit_array):
        force_debug = True
        if force_debug: print("byte", self.byte_pointer, "bit", self.bit_pointer, "in_len", len(bit_array))
        if self.write_mode == -1:
            raise Exception("BitSequenceFile could not write to file: file was opened for reading")
        if not isinstance(bit_array, BitArray):
            raise Exception("BitSequenceFile.write accepts only BitArray instances as argument")
        self.file.seek(self.byte_pointer)

        if (not self.bit_pointer) and bit_array.byte_closed:
            #якщо у файлі вказівник на нульовому біті та довжина послідовності біт кратна 8 -- записати напряму в файл без перетворень
            if force_debug: print("bytewise writing", bit_array.bytes)
            try:
                self.file.write(bit_array.bytes)
            except:
                raise Exception("BitSequenceFile failed to write into the file")
            self.byte_pointer += len(bit_array.bytes)
            self.opened_byte = 0
            return 0

        elif (not self.bit_pointer) and (not bit_array.byte_closed):

            #якщо у файлі вказівник на нульовому біті, але довжина послідовності біт не кратна 8 -- записати напряму в файл всі окрім останнього байта, в останньому байті занулити усі незначущі біти
            try:
                if len(bit_array.bytes) > 1:
                    self.file.write(bit_array.bytes[:-1])
                    if force_debug: print("bytewise writing*", bytewise_string(bit_array.bytes))
                self.file.write(bytes([bit_array.bytes[-1] & (2**bit_array.bit_pointer-1)]))
                if force_debug: print("bitwise writing", bytewise_string(bytes([bit_array.bytes[-1] & (2**bit_array.bit_pointer-1)])))
            except:
                raise Exception("BitSequenceFile failed to write into the file")
            self.byte_pointer += len(bit_array.bytes) - 1
            self.bit_pointer = bit_array.bit_pointer
            self.opened_byte = bit_array.bytes[-1] & (2**bit_array.bit_pointer-1)
            return 0

        else:
            #якщо у файлі вказівник не на нульовому біті
            try:
                # дозапис в поточний байт
                if force_debug: print("existing byte", bytewise_string(bytes([self.opened_byte & (2 ** self.bit_pointer - 1)])))
                if force_debug: print("appending", bytewise_string(bytes([bit_array.bytes[0]])))
                if force_debug: print("shifted and clamped", bytewise_string(bytes([((bit_array.bytes[0] << (self.bit_pointer)) & (2 ** 8 - 2 ** self.bit_pointer))])))
                if force_debug: print("writing", bytewise_string(bytes([(self.opened_byte & (2 ** self.bit_pointer - 1) )+ ((bit_array.bytes[0] << (self.bit_pointer)) & (2 ** 8 - 2 ** self.bit_pointer))])))
                self.file.write(bytes([(self.opened_byte & (2 ** self.bit_pointer - 1))+ ((bit_array.bytes[0] << (self.bit_pointer)) & (2 ** 8 - 2 ** self.bit_pointer))]))
                self.opened_byte = (self.opened_byte & (2 ** self.bit_pointer - 1)) + ((bit_array.bytes[0] << (self.bit_pointer)) & (2 ** 8 - 2 ** self.bit_pointer))
                self.byte_pointer += (len(bit_array) + self.bit_pointer) > 7
                new_bit_pointer = (self.bit_pointer + len(bit_array))%8
                if len(bit_array) - (8-self.bit_pointer) > 7:
                    # запис повних байтів
                    shifted_bytes_a = bytes([
                        bit_array.bytes[i] >> (8 - self.bit_pointer)
                        for i in range(len(bit_array.bytes) - 1)])
                    shifted_bytes_b = bytes([
                        (bit_array.bytes[i + 1] << self.bit_pointer) & (2 ** 8 - 2 ** self.bit_pointer)
                        for i in range(len(bit_array.bytes) - 1)])

                    shifted_bytes = bytes([shifted_bytes_a[i] + shifted_bytes_b[i] for i in range(len(shifted_bytes_a))])
                    if force_debug: print("byte shift", bytewise_string(shifted_bytes))
                    self.file.write(shifted_bytes)
                    self.byte_pointer += len(shifted_bytes)
                    self.opened_byte = 0
                    new_bit_pointer = 0
                # запис неповного останнього байта:
                    if (len(bit_array) + self.bit_pointer)%8 and len(bit_array)>8-self.bit_pointer:
                        if force_debug: print("tail", bytewise_string(bytes([bit_array.bytes[-1] >> (8-self.bit_pointer)])))
                        self.file.write(bytes([bit_array.bytes[-1] >> (8-self.bit_pointer)]))
                        new_bit_pointer = (len(bit_array) + self.bit_pointer)%8
                        if new_bit_pointer:
                            self.opened_byte = bit_array.bytes[-1] >> (self.bit_pointer)
                        else:
                            self.byte_pointer += 1
                elif self.bit_pointer + len(bit_array) > 8:
                    tail_byte = 0
                    if len(bit_array) > 8:
                        tail_byte += bit_array.bytes[-2] >> (8 - self.bit_pointer)
                        if force_debug: print("left tail", bytewise_string(bytes([tail_byte])))
                        tail_byte += (bit_array.bytes[-1] << self.bit_pointer) & (2 ** 8 - 2 ** self.bit_pointer)
                    else:
                        tail_byte += bit_array.bytes[-1] >> (8 - self.bit_pointer)

                    self.file.write(bytes([tail_byte]))

                    if force_debug: print("elif tail", bytewise_string(bytes([tail_byte])))
                    new_bit_pointer = (len(bit_array) + self.bit_pointer) % 8
                    if new_bit_pointer:
                        self.opened_byte = tail_byte
                    else:
                        self.byte_pointer += 1

                self.bit_pointer = new_bit_pointer



            except:
                raise Exception("BitSequenceFile failed to write into the file")


    def close(self):
        try:
            self.file.close()
        except:
            raise Exception("BitSequenceFile failed to close file")
