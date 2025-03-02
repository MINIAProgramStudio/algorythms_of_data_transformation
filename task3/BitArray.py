import copy

def bytewise_string(in_bytes):
    if isinstance(in_bytes, int):
        in_bytes = bytes([in_bytes])
    output = ""
    for byte in in_bytes:
        output += format(byte, '08b') + " "
    return output


class BitArray:
    def __init__(self, in_bytes, bit_pointer):
        if not len(in_bytes):
            in_bytes = bytearray([0])
        if isinstance(in_bytes, bytearray):
            self.bytes = in_bytes
        else:
            self.bytes = bytearray(in_bytes)
        self.bytes[-1] = in_bytes[-1] & (2**bit_pointer -1) # занулити біти після вказівника

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
        return max(len(self.bytes)*8 - (8 * (not self.byte_closed)) + self.bit_pointer,0)


    def __rshift__(self, other: int):
        force_debug = False
        if not isinstance(other, int):
            raise Exception("TYPE_ERROR: BitArray can shift bits only by int")
        if other < 0:
            raise Exception("VALUE_ERROR: BitArray can shift bits only by positive integer or zero")
        output = self.copy()
        if force_debug: print("rshift received request: ", other)
        if other > 7: # якщо довжина зсуву більше одного байта -- викидаємо зайві байти на початку і переходимо до зсуву на відстань менше 8 біт
            if other//8 < len(output.bytes): # якщо довжина (в байтах) зсуву менше ніж кількість байтів -- викидаємо зайві байти на початку
                if force_debug: print("cutting", other//8, "bytes")
                output.bytes = output.bytes[other//8:]
                other %= 8
                if force_debug: print("len bytes after cut", len(output.bytes))
            else: # якшо довжина (в байтах) зсуву більше ніж кількість байтів -- повернути пустий BitArray
                return BitArray(bytearray([0]),0)
        if other: # якщо залишкова довжина зсуву не нуль
            remains = bytearray([
                byte>>other for byte in output.bytes
            ]) # залишок від існуючих байтів
            transfer = bytearray([
                (byte<<(8-other))&255 for byte in output.bytes
            ]) # шматки байтів які треба зсунути в попередній байт
            if len(remains) > 1:
                output.bytes = bytearray([
                    remains[i] + transfer[i+1] for i in range(len(remains) -1)
                ]) # сума залишків та шматків наступних байтів
                output.bytes += bytearray([remains[-1]]) # останній залишок, що не має відповідного шматка наступного байту
            else:
                output.bytes = bytearray([remains[-1]])  # оскільки байт один, то наступного байту не існує і зсувати з нього в цей один байт нічого
            if output.byte_closed:
                output.bit_pointer = 8 - other # вказівник на незаповнений біт
            else:
                output.bit_pointer -= other # вказівник на незаповнений біт зменшуємо на довжину зсуву

            if output.bit_pointer < 0: # якщо вказівник перейшов на попередній байт
                if len(output.bytes)>1: # якщо щонайменше 2 байти
                    output.bytes = output.bytes[:-1] # викинути останній байт
                    output.bit_pointer %= 8 # оскільки останній байт викинуто, вказівник беремо за модулем і тепер він вказує на біт в останньому наявному байті
                else: # якщо байт один, а вказівник менше 0, значить потрібно повернути пустий BitArray
                    output.bytes = bytearray([0])
                    output.bit_pointer = 0
            output.byte_closed = False # оскільки максимальна довжина бітового зсуву після байтового зсуву 7 і вказівник був менший за нуль, то останній байт не може бути закритим
        if force_debug: print(output.bytes, output.bit_pointer, output.byte_closed)
        return output

    def __lshift__(self, other):
        force_debug = False
        if not isinstance(other, int):
            raise Exception("TYPE_ERROR: BitArray can shift bits only by int")
        if other < 0:
            raise Exception("VALUE_ERROR: BitArray can shift bits only by positive integer or zero")
        output = self.copy()
        if other > 7: # якщо довжина зсуву більше одного байта -- дописати в початок нульові байти і перейти до зсуву на відстань менше 8 біт
            output.bytes = bytearray([0]*(other//8)) + output.bytes
            other %= 8
        if other: # якщо залишкова довжина зсуву не нуль
            remains = bytearray([
                (byte<<other)&255 for byte in output.bytes
            ]) # залишок від існуючих байтів
            transfer = bytearray([
                byte>>(8-other) for byte in output.bytes
            ]) # шматки байтів які треба зсунути в наступний байт
            if force_debug: print("remains",bytewise_string(remains))
            if force_debug: print("transfer",bytewise_string(transfer))
            if len(remains) > 1:
                output.bytes = bytearray([remains[0]]) # залишки першого байта
                if force_debug: print("first byte remains", bytewise_string(output.bytes))
                output.bytes += bytearray([
                    transfer[i-1] + remains[i] for i in range(1,len(transfer))
                ])
                if force_debug: print("remains+transfer", bytewise_string(output.bytes))
                if ((output.bit_pointer+other) % 8 and output.bit_pointer+other > 7) or self.byte_closed:
                    output.bytes += bytearray([transfer[-1]]) # якщо відбувся перехід в наступний байт -- додати байт для залишку з останнього (а тепер передостаннього) байта
                    if force_debug: print("transfer", bytewise_string(output.bytes))
                    output.bit_pointer += other
                    if output.bit_pointer % 8:  # якщо вказівник не на початку байта -- позначити останній байт як відкритий
                        output.bit_pointer %= 8
                        output.byte_closed = False
                    else:  # оскільки вказівник на початку байта і максимальна довжина бітового зсуву 7, то значить останній байт записано повністю
                        output.bit_pointer = 0
                        output.byte_closed = True
                else:
                    output.bit_pointer += other
                    if output.bit_pointer % 8:  # якщо вказівник не на початку байта -- позначити останній байт як відкритий
                        output.bit_pointer %= 8
                        output.byte_closed = False
                    else:  # оскільки вказівник на початку байта і максимальна довжина бітового зсуву 7, то значить останній байт записано повністю
                        output.bit_pointer = 0
                        output.byte_closed = True
            else:
                if output.bit_pointer + output.byte_closed*8 + other > 8:
                    output.bytes = bytearray([remains[0]]) + bytearray([transfer[0]]) # якщо довжина BitArray була менше одного байта, а зсув перейшов в наступний, то вихідний BitArray має два байти: залишок першого байта і шматок першого байта
                else:
                    output.bytes = bytearray([remains[0]]) # якщо довжина itArray була менше одного байта і зсув не перейшов в наступний байт, то вихідний BitArray міститиме лише зсунутий оригінальний байт
                output.bit_pointer += other
                if output.bit_pointer%8: # якщо вказівник не на початку байта -- позначити останній байт як відкритий
                    output.bit_pointer %= 8
                    output.byte_closed = False
                else: #оскільки вказівник на початку байта і максимальна довжина бітового зсуву 7, то значить останній байт записано повністю
                    output.bit_pointer = 0
                    output.byte_closed = True
        if force_debug: print(bytewise_string(output.bytes), output.bit_pointer, output.byte_closed)
        return output

    def __repr__(self):
        return str(self)

    def concat(self, right):
        force_debug = False
        if self.bit_pointer:
            shifted = right<<self.bit_pointer # якщо ліва частина не завершується повним байтом -- зсунути праву частину
            if force_debug: print("shifted", shifted)
            pointer = self.bit_pointer + right.bit_pointer
            if force_debug: print("pointer", pointer)
            if pointer>8:
                pointer %= 8
            if len(self)>8: # зробити конкатинацію відповідно до довжин лівої та правої частин
                if len(shifted)>8:
                    if force_debug: print("ll")
                    return BitArray(self.bytes[:-1]+ bytearray([int(self.bytes[-1] + shifted.bytes[0])]) + shifted.bytes[1:], pointer)
                else:
                    if force_debug: print("ls")
                    return BitArray(self.bytes[:-1] + bytearray([int(self.bytes[-1] + shifted.bytes[0])]), pointer)
            else:
                if len(shifted)>8:
                    if force_debug: print("sl")
                    return BitArray(bytearray([int(self.bytes[-1] + shifted.bytes[0])]) + shifted.bytes[1:], pointer)
                else:
                    if force_debug: print("ss")
                    return BitArray(bytearray([int(self.bytes[-1] + shifted.bytes[0])]), pointer)
        else:
            if self.byte_closed: # якщо останній байт закритий (ліва бітова послідовність існує) зробити конкатинацію
                pointer = right.bit_pointer
                if pointer == 0:
                    pointer = 8
                return BitArray(self.bytes + right.bytes, pointer)
            else:
                return right.copy() # якщо останній байт відкритий (ліва бітова послідовність НЕ існує) -- повернути праву частину

    def self_concat(self, right):
        force_debug = False
        if self.bit_pointer:
            shifted = right << self.bit_pointer  # якщо ліва частина не завершується повним байтом -- зсунути праву частину
            if force_debug: print("shifted", shifted)
            pointer = self.bit_pointer + right.bit_pointer
            if force_debug: print("pointer", pointer)
            if pointer > 8:
                pointer %= 8
            if len(self) > 8:  # зробити конкатинацію відповідно до довжин лівої та правої частин
                if len(shifted) > 8:
                    if force_debug: print("ll")
                    self.bytes[-1] = int((self.bytes[-1]&(2**self.bit_pointer-1)) + shifted.bytes[0])
                    self.bytes += shifted.bytes[1:]
                    self.bit_pointer = pointer % 8
                    self.byte_closed = pointer == 8
                else:
                    if force_debug: print("ls")
                    self.bytes[-1] = int((self.bytes[-1]&(2**self.bit_pointer-1)) + shifted.bytes[0])
                    self.bit_pointer = pointer % 8
                    self.byte_closed = pointer == 8
            else:
                if len(shifted) > 8:
                    if force_debug: print("sl")
                    self.bytes = bytearray([int((self.bytes[-1]&(2**self.bit_pointer-1)) + shifted.bytes[0])]) + shifted.bytes[1:]
                    self.bit_pointer = pointer % 8
                    self.byte_closed = pointer == 8
                else:
                    if force_debug: print("ss")
                    self.bytes = bytearray([int((self.bytes[-1]&(2**self.bit_pointer-1)) + shifted.bytes[0])])
                    self.bit_pointer = pointer % 8
                    self.byte_closed = pointer == 8
        else:
            if self.byte_closed:  # якщо останній байт закритий (ліва бітова послідовність існує) зробити конкатинацію
                pointer = right.bit_pointer
                if pointer == 0:
                    pointer = 8
                self.bytes = self.bytes + right.bytes
                self.bit_pointer = pointer%8
                self.byte_closed = pointer == 8
            else:
                self.bytes = bytearray(right.bytes)
                self.bit_pointer = right.bit_pointer
                self.byte_closed = right.byte_closed



    def __eq__(self, other):
        if (
            self.bytes == other.bytes
        ) and (
            self.bit_pointer == other.bit_pointer
        ) and (
            self.byte_closed == other.byte_closed
        ):
            return True # Бітові послідовності рівні тоді і тільки тоді, коли їх байти та вказівники рівні.
        else:
            return False

    def __hash__(self):
        return hash(bytes(self.bytes)) #Геш бітової послідовності рівний гешу її байтів

    def __getitem__(self, key):
        force_debug = False
        light_debug = False
        if isinstance(key, int): # якщо потрібно отримати один біт
            if force_debug or light_debug: print(key)
            if key >= len(self):
                raise IndexError("Index outside of BitArray, recieved " + str(key) + " while length is " + str(len(self)))
            elif key >= 0:
                byte = self.bytes[key//8] # вибираємо необхідний байт
                bit = (byte>>(key%8))&1 # ставимо біт на нульову позицію
                return BitArray(bytearray([bit]), 1) # повертаємо біт в BitArray
            else:
                byte = self.bytes[(len(self) - key) // 8]
                bit = (byte >> ((8-key) % 8)) & 1
                return BitArray(bytearray([bit]), 1)
        elif isinstance(key, slice): # Якщо потрібно отримати підпослідовність (крок завжди 1)
            key = key.indices(len(self))
            key[0]
            key[1]
            bit_pointer = key[1]%8
            if bit_pointer == 0 and key[1]>0:
                bit_pointer = 8
            if force_debug or light_debug: print(key[0], key[1], bit_pointer)
            output = self.copy()
            if force_debug: print(output)
            output.bytes = output.bytes[:key[1] // 8 + int((key[1]%8)>0)] # залишити лише ті байти які йдуть перед кінцем послідовності
            if force_debug: print(output)
            if len(output.bytes) > 1:
                output.bytes[-1] = output.bytes[-1] & (2 ** bit_pointer - 1) # занулити біти, що не використовуються в останньому байті
            elif len(output.bytes) == 1:
                if force_debug: print(output.bytes[0], bin(2 ** bit_pointer - 1))
                output.bytes = bytearray([output.bytes[0] & (2 ** bit_pointer - 1)]) # занулити біти, що не використовуються в останньому байті
            output.bit_pointer = key[1]%8
            if output.bit_pointer == 0 and key[1]>0:
                output.byte_closed = True
            else:
                output.byte_closed = False
            if key[0]:
                if force_debug: print("requestet rshift", key[0])
                output = output>>key[0] # змістити бітову підпослідовність на початок послідовності

            if force_debug: print(output, output.bit_pointer, output.byte_closed)
            if force_debug: print()
            return output

    def get_bit(self, key):
        if key >= len(self):
            raise IndexError("Index outside of BitArray, recieved " + str(key) + " while length is " + str(len(self)))
        elif key >= 0:
            byte = self.bytes[key // 8]  # вибираємо необхідний байт
            bit = (byte >> (key % 8)) & 1  # ставимо біт на нульову позицію
            if bit:
                return True
            else:
                return False
        else:
            byte = self.bytes[(len(self) - key) // 8]
            bit = (byte >> ((8 - key) % 8)) & 1
            if bit:
                return True
            else:
                return False

    def append_bit(self, bit):
        if bit:
            if self.byte_closed:
                self.bytes += bytearray([1])
                self.bit_pointer = 1
                self.byte_closed = False
            else:
                self.bytes[-1] += (2 ** self.bit_pointer)
                self.bit_pointer += 1
                self.byte_closed = self.bit_pointer == 8
                self.bit_pointer %= 8

        else:
            if self.byte_closed:
                self.bytes += bytearray([0])
                self.bit_pointer = 1
                self.byte_closed = False
            else:
                self.bit_pointer += 1
                self.byte_closed = self.bit_pointer == 8
                self.bit_pointer %= 8

    def copy(self):
        return BitArray(bytearray(self.bytes), self.bit_pointer + self.byte_closed*8)

"""    
    def __and__(self, other):
        total_length = max(len(self), len(other))
"""