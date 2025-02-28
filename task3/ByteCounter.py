from BitSequenceFile import BitSequenceFile, bytewise_string
from BitArray import BitArray
from PythonTableConsole import PythonTableConsole

class ByteCounter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.counter = dict()
    def count_bytes(self):
        bsf = BitSequenceFile(self.file_path)
        counter = dict()
        for i in range(0,256):
            counter[i] = 0
        while True:
            bit_array = bsf.read(8)
            if not bit_array.byte_closed:
                break
            segment = bit_array.bytes[0]
            counter[segment] += 1
        self.counter = counter
        return counter

    def __repr__(self):
        if self.counter.keys():
            counter_list = [["byte"],["counter"]]
            for key in self.counter.keys():
                if self.counter[key]:
                    counter_list[0].append(bytewise_string(key))
                    counter_list[1].append(self.counter[key])
            table = PythonTableConsole(counter_list)
            table.sort_by_column(1,1)
            return str(table)
        else:
            return "ByteCounter: Bytes have not been counted"
