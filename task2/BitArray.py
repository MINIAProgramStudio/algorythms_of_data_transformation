import copy

class BitArray:
    def __init__(self, in_bytes, bit_pointer):
        if len(in_bytes) > 1: # якщо байтів щонайменше 2 -- занулити біти в останньому байті, що йдуть не перед вказівником
            self.bytes = in_bytes[:-1] + bytes([in_bytes[-1] & (2**bit_pointer -1)])
        elif len(in_bytes) == 1: # якщо байт один -- занулити біти в ньому, що йдуть не перед вказівником
            self.bytes = bytes([in_bytes[0] & (2**bit_pointer -1)])

        self.byte_closed = bit_pointer == 8 # якщо передано вказівник 8, значить останній байт повністю використаний

        if self.byte_closed: # якщо останній байт повністю використаний, занулити вказівник (вказівник має бути в межах 0-7)
            self.bit_pointer = 0
        else:
            self.bit_pointer = bit_pointer


    def __str__(self):
        output = ""
        for byte in self.bytes: # для кожного байту отримати його текстову репрезентацію та прочитати її справа наліво, тобто навпаки
            output += format(byte, '08b')[::-1]
        return output[:len(self)] # обрізати вихідний рядок до кількості бітів

    def __len__(self):
        """
        Якщо останній байт повністю використаний, повернути кількість байтів помножену на 8
        Якщо останній байт не повністю використаний, повернути кількість байтів помножену на 8 мінус 8 плюс вказівник (кількість біт в повних байтах та кількість біт в неповному байті)
        """
        return len(self.bytes)*8 - (8 * (not self.byte_closed)) + self.bit_pointer


    def __rshift__(self, other: int):
        if not isinstance(other, int):
            raise Exception("TYPE_ERROR: BitArray can shift bits only by int")
        if other < 0:
            raise Exception("VALUE_ERROR: BitArray can shift bits only by positive integer or zero")
        output = copy.deepcopy(self)
        if other > 7: # якщо довжина зсуву більше одного байта -- викидаємо зайві байти на початку і переходимо до зсуву на відстань менше 8 біт
            if other//8 < len(output.bytes): # якщо довжина (в байтах) зсуву менше ніж кількість байтів -- викидаємо зайві байти на початку
                output.bytes = output.bytes[other//8:]
                other %= 8
            else: # якшо довжина (в байтах) зсуву більше ніж кількість байтів -- повернути пустий BitArray
                return BitArray(bytes([0]),0)
        if other: # якщо залишкова довжина зсуву не нуль
            remains = bytes([
                byte>>other for byte in output.bytes
            ]) # залишок від існуючих байтів
            transfer = bytes([
                (byte<<(8-other))%256 for byte in output.bytes
            ]) # шматки байтів які треба зсунути в попередній байт
            if len(remains) > 1:
                output.bytes = bytes([
                    remains[i] + transfer[i+1] for i in range(len(remains) -1)
                ]) # сума залишків та шматків наступних байтів
                output.bytes += bytes([remains[-1]]) # останній залишок, що не має відповідного шматка наступного байту
            else:
                output.bytes = bytes([remains[-1]])  # оскільки байт один, то наступного байту не існує і зсувати з нього в цей один байт нічого
            output.bit_pointer -= other # вказівник на незаповнений біт зменшуємо на довжину зсуву
            if output.bit_pointer < 0: # якщо вказівник перейшов на попередній байт
                if len(output.bytes)>1: # якщо щонайменше 2 байти
                    output.bytes = output.bytes[:-1] # викинути останній байт
                    output.bit_pointer %= 8 # оскільки останній байт викинуто, вказівник беремо за модулем і тепер він вказує на біт в останньому наявному байті
                    output.byte_closed = False # оскільки максимальна довжина бітового зсуву після байтового зсуву 7 і вказівник був менший за нуль, то останній байт не може бути закритим
                else: # якщо байт один, а вказівник менше 0, значить потрібно повернути пустий BitArray
                    output.bytes = bytes([0])
                    output.bit_pointer = 0
                    output.byte_closed = False
        return output

    def __lshift__(self, other):
        force_debug = False
        if not isinstance(other, int):
            raise Exception("TYPE_ERROR: BitArray can shift bits only by int")
        if other < 0:
            raise Exception("VALUE_ERROR: BitArray can shift bits only by positive integer or zero")
        output = copy.deepcopy(self)
        if other > 7: # якщо довжина зсуву більше одного байта -- дописати в початок нульові байти і перейти до зсуву на відстань менше 8 біт
            output.bytes = bytes([0]*(other//8)) + output.bytes
            other %= 8
        if other: # якщо залишкова довжина зсуву не нуль
            remains = bytes([
                (byte<<other)%256 for byte in output.bytes
            ]) # залишок від існуючих байтів
            transfer = bytes([
                byte>>(8-other) for byte in output.bytes
            ]) # шматки байтів які треба зсунути в наступний байт
            if len(remains) > 1:
                output.bytes = bytes([remains[0]]) # залишки першого байта
                if force_debug: print("first byte remains", output)
                output.bytes += bytes([
                    transfer[i-1] + remains[i] for i in range(1,len(transfer))
                ])
                if force_debug: print("remains+transfer", output)
                if output.bit_pointer + other > 7:
                    output.bytes += bytes([transfer[-1]]) # якщо відбувся перехід в наступний байт -- додати байт для залишку з останнього (а тепер передостаннього) байта
                    if force_debug: print("transfer", output)
                    output.bit_pointer += other
                    if output.bit_pointer % 8:  # якщо вказівник не на початку байта -- позначити останній байт як відкритий
                        output.bit_pointer %= 8
                        output.byte_closed = False
                    else:  # оскільки вказівник на початку байта і максимальна довжина бітового зсуву 7, то значить останній байт записано повністю
                        output.bit_pointer = 0
                        output.byte_closed = False
                else:
                    output.bit_pointer += other
                    if output.bit_pointer % 8:  # якщо вказівник не на початку байта -- позначити останній байт як відкритий
                        output.bit_pointer %= 8
                        output.byte_closed = False
                    else:  # оскільки вказівник на початку байта і максимальна довжина бітового зсуву 7, то значить останній байт записано повністю
                        output.bit_pointer = 0
                        output.byte_closed = True
            else:
                if output.bit_pointer + other > 7:
                    output.bytes = bytes([remains[0]]) + bytes([transfer[0]]) # якщо довжина BitArray була менше одного байта, а зсув перейшов в наступний, то вихідний BitArray має два байти: залишок першого байта і шматок першого байта
                else:
                    output.bytes = bytes([remains[0]]) # якщо довжина itArray була менше одного байта і зсув не перейшов в наступний байт, то вихідний BitArray міститиме лише зсунутий оригінальний байт
                output.bit_pointer += other
                if output.bit_pointer%8: # якщо вказівник не на початку байта -- позначити останній байт як відкритий
                    output.bit_pointer %= 8
                    output.byte_closed = False
                else: #оскільки вказівник на початку байта і максимальна довжина бітового зсуву 7, то значить останній байт записано повністю
                    output.bit_pointer = 0
                    output.byte_closed = True
        return output




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