import os

from BitArray import BitArray, bytewise_string



class BitSequenceFile:
    def __init__(self, file_path, write_mode = -1):
        self.bit_pointer = 0 # points to the unread/unwritten bit in unresolved byte
        self.byte_pointer = 0 # points to the position of the unresolved byte
        self.write_mode = write_mode
        self.file_path = file_path
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
                self.file_length = os.path.getsize(file_path)
        except:
            raise Exception("BitSequenceFile could not open file specified")

    def read(self, bits = None):
        if bits is None:
            bits = self.file_length*8
        if self.byte_pointer*8 + self.bit_pointer + bits > self.file_length * 8:
            bits = self.file_length - (self.byte_pointer*8 + self.bit_pointer)
            if bits < 0:
                return BitArray(bytearray([0]), 0)
        if self.write_mode != -1:
            raise Exception("BitSequenceFile could not read file: file was opened for writing")
        self.file.seek(self.byte_pointer) # перейти в відкритий байт
        raw_bytes = self.file.read((bits+self.bit_pointer)//8 + ((bits+self.bit_pointer)%8 > 0)) # байти в яких містяться необхідні біти
        if self.bit_pointer + bits > 7 and (self.bit_pointer + bits) % 8 == 0:
            bit_array = BitArray(raw_bytes, 8) # якщо бітова послідовність завершується повним байтом
        else:
            bit_array = BitArray(raw_bytes, (self.bit_pointer + bits)%8) # якщо бітова послідовність завершується НЕ повним байтом
        bit_array = bit_array >> self.bit_pointer # зсунути бітову послідовність на початок BitArray
        self.bit_pointer += bits
        self.byte_pointer += self.bit_pointer//8
        self.bit_pointer %= 8
        return bit_array

    def write(self, bit_array):
        starting_length = len(bit_array)
        force_debug = False
        if force_debug: print("write input", bytewise_string(bit_array.bytes), "len", starting_length)
        if force_debug: print("exsiting byte", bytewise_string(bytearray([self.opened_byte])))
        if force_debug: print("byte", self.byte_pointer, "bit", self.bit_pointer)
        if self.write_mode == -1:
            raise Exception("BitSequenceFile could not write to file: file was opened for reading")
        if not isinstance(bit_array, BitArray):
            raise Exception("BitSequenceFile.write accepts only BitArray instances as argument")
        self.file.seek(self.byte_pointer) # перейти в відкритий байт
        try:
            bit_array = bit_array<<self.bit_pointer # зсунути послідовність біт так, щоб вона починалась на вказівнику
            if force_debug: print("write shifted", bytewise_string(bit_array.bytes), "len", len(bit_array))
            if len(bit_array) > 8:
                bit_array.bytes[0] = bit_array.bytes[0] + self.opened_byte

            else:
                bit_array.bytes = bytearray([bit_array.bytes[0]  + self.opened_byte])
            if force_debug: print("write existing + new", bytewise_string(bit_array.bytes), "len", len(bit_array))
            self.file.write(bit_array.bytes)
            self.bit_pointer += starting_length
            self.byte_pointer += self.bit_pointer // 8
            self.bit_pointer %= 8
            if self.bit_pointer: self.opened_byte = bit_array.bytes[-1]
            else: self.opened_byte = 0

        except:
            raise Exception("BitSequenceFile failed to write into the file")


    def close(self):
        try:
            self.file.close()
        except:
            raise Exception("BitSequenceFile failed to close file")
