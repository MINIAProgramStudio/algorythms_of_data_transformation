from BitSequenceFile import BitSequenceFile, bytewise_string
from BitArray import BitArray
from PythonTableConsole import PythonTableConsole

class ByteCounter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.counter = {}
    def count_bytes(self):
        bsf = BitSequenceFile(self.file_path)
        counter = {}
        for i in range(0,256): # створити ключі для кожного байта
            counter[i] = 0
        while True:
            bit_array = bsf.read(8) #прочитати байт
            if not bit_array.byte_closed: # якщо повернуто пусту послідовність -- кінець файла
                break
            segment = bit_array.bytes[0] # дістати значення байта
            counter[segment] += 1 # збільшити лічильник для байта на 1
        self.counter = counter # зберегти таблицю лічильників
        return counter # повернути таблицю лічильників

    def __repr__(self):
        if self.counter.keys():
            counter_list = [["byte"],["counter"]] # створити заголовки колонок
            for key in self.counter.keys(): # для кожного різного байта
                if self.counter[key]:
                    counter_list[0].append(bytewise_string(key)) # записати бітову репрезентацію байта в колонку byte
                    counter_list[1].append(self.counter[key]) # записати значення лічильника байта в колону counter
            table = PythonTableConsole(counter_list) # створити таблицю з list
            table.sort_by_column(1,1) # сортувати за лічильниками
            return str(table) # повернути текстову репрезентацію таблиці
        else:
            return "ByteCounter: Bytes have not been counted"
