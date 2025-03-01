from BitArray import BitArray, bytewise_string
from ByteCounter import ByteCounter
import copy
from time import time
import warnings
from tqdm import tqdm

class HuffmanTree:
    def __init__(self, source):
        if isinstance(source, ByteCounter):
            self.byte_counter = source # зберегти
            self.build()
        else:
            self.byte_counter = None
            self.nodes = {}


    def build(self, recount = True):
        force_debug = False
        if not (self.byte_counter is None):
            if recount: self.byte_counter.count_bytes()
            self.nodes = copy.deepcopy(self.byte_counter.counter) # початкові вершини дерева, вони ж листки, це копії лічильників
            if force_debug: print(len(self.nodes.keys()), self.nodes)
            for key in range(0, 256):
                if self.nodes[key]:
                    self.nodes[key] = [self.nodes[key], None, None, None] # вершина кодується за схемою: значення байта або ключа розвилки: [його кількість у файлі, дитина_0, дитина_1, батьківська вершина]
                else:
                    del(self.nodes[key]) # видалити байт з списка вершин, якщо він не зустрічався в файлі
            if force_debug: print(len(self.nodes.keys()), self.nodes)
            n_bytes = len(self.nodes.keys()) # кількість різних байтів які зустрічалися у файлі
            opened_nodes = copy.deepcopy(self.nodes) # список вершин, доступних для об'єднання (відкриті вершини)
            node_key = list(opened_nodes.keys())[0] # fail safe на випадок, якщо у файлі всі байти однакові
            for i in range(n_bytes-1): # потрібно об'єднати відкриті вершини, кожне об'єднання зменшує кількість відкритих вершин на 1, отже треба зробити n_bytes-1 об'єднань
                if force_debug: print(i, len(opened_nodes), opened_nodes)
                if force_debug: print(i, len(opened_nodes), opened_nodes)
                lowest = min(t[0] for t in list(opened_nodes.values())) # найменше значення лічильника в відкритих вершинах
                if force_debug: print(lowest)
                lowest_keys = [key for key in opened_nodes.keys() if opened_nodes[key][0] == lowest] #ключі відкритих вершин, що мають найменше значення
                if force_debug: print(lowest_keys)
                if len(lowest_keys) > 1: # якщо ключів відкритих вершин з найменшим значенням декілька -- об'єднуємо перші дві з них
                    key_a = lowest_keys[0] # запам'ятовуємо ключі вершин
                    key_b = lowest_keys[1]
                    del(opened_nodes[key_a])
                    del(opened_nodes[key_b])
                else: # якщо лише один ключ з найменшим значенням -- запам'ятовуємо її, шукаємо другий найменший ключ та об'єднуємо їх
                    key_a = lowest_keys[0]
                    del(opened_nodes[key_a])
                    lowest = min(t[0] for t in list(opened_nodes.values()))
                    if force_debug: print("e", lowest)
                    lowest_keys = [key for key in opened_nodes if opened_nodes[key][0] == lowest]
                    if force_debug: print(lowest_keys)
                    key_b = lowest_keys[0]
                    del (opened_nodes[key_b])
                node_key = 0b100000000 + i # ключ розгалужень в діапазоні 256-511
                node_value = self.nodes[key_a][0] + self.nodes[key_b][0] # вага розгалуженя рівна вазі двох дочірніх вершин
                self.nodes[node_key] = [node_value, key_a, key_b, None] # створюємо нове розгалуження
                self.nodes[key_a][3] = node_key # записуємо нову вершину як батька дочірніх вершин
                self.nodes[key_b][3] = node_key
                opened_nodes[node_key] = [node_value, key_a, key_b, None] # створюємо нове розгалуження, як відкриту вершину
                if force_debug: print()
            if force_debug: print(self.nodes)
            if force_debug: print(opened_nodes)
            self.root_key = node_key # запам'ятовуємо ключ найпізнішого об'єднання, як корінь дерева
        self.create_encoding_lookup() # запит створення таблиці кодування
        self.create_decoding_lookup() # запит створення таблиці декодування

    def create_encoding_lookup(self):
        force_debug = False
        if force_debug: print("creating encoding lookup")
        encoding_lookup = {}
        for key in self.nodes: # для кожної вершини в дереві
            if key > 255:
                continue # якщо обраний запис не байт (відповідно не лист) -- нічого не робити
            code = BitArray(bytes([0]), 0) # створюємо пустий бітовий рядок
            selected_key = key
            while True:
                parent_key = self.nodes[selected_key][3]
                if force_debug: print(selected_key, parent_key)
                if self.nodes[parent_key][1] == selected_key: # якщо ліва дитина -- записуємо 0 в бітовий рядок
                    code = BitArray(bytes([0]),1).concat(code)
                elif self.nodes[parent_key][2] == selected_key: # якщо права дитина -- записуємо 1 в бітовий рядок
                    code = BitArray(bytes([1]),1).concat(code)
                else:
                    raise Exception("HuffmanTree: node has parent that does not have said node as a child")
                if force_debug: print(key, code)
                selected_key = parent_key # переходимо до батьківської вершини
                if selected_key == self.root_key: # якщо дійшли до кореня -- завершуємо
                    break
            encoding_lookup[key] = code # записуємо код в таблицю
            if force_debug: print()
        self.encoding_lookup = encoding_lookup # зберігаємо таблицю

    def encode(self, object):
        force_debug = False
        time_debug = False
        if time_debug: seeking_time, concat_time = 0,0
        if isinstance(object, int): # якщо кодуємо один байт
            if object > 255 or object < 0:
                raise Exception("HuffmanTree can encode only integers 0-255 and bytes")
            return self.encoding_lookup[object] # повернути бітовий рядок, що відповідає байту
        elif isinstance(object, bytes): # якщо кодуємо байти
            output = BitArray([0],0)
            for byte in object: # для кожного байта з послідовності
                code = self.encoding_lookup[byte] # знайти код байта
                output = output.concat(code) # записати код байта в кінець послідовності
            return output
        elif isinstance(object, BitArray): # див. кодування байтів
            output = BitArray([0], 0)
            for byte in object.bytes:
                if force_debug: print("looking for", bytewise_string(byte))
                if time_debug: seeking_time -= time()
                code = self.encoding_lookup[byte]
                if time_debug: seeking_time += time()
                if force_debug: print("code", code)
                if time_debug: concat_time -= time()
                output.self_concat(code)
                #for bit_pos in range(len(code)):
                    #output.append_bit(code.get_bit(bit_pos))
                if time_debug: concat_time += time()
                if force_debug: print("output",output)
                if force_debug: print()
            if time_debug: print("encoding seeking time", seeking_time, "s")
            if time_debug: print("encoding concat time ", concat_time, "s")
            return output
        else:
            raise Exception("HuffmanTree can encode only integers 0-255 and bytes")

    def create_decoding_lookup(self):
        force_debug = False
        if force_debug: print("creating decoding lookup")
        decoding_lookup = {}
        for key in self.encoding_lookup.keys():
            if force_debug:print(key, bytewise_string(self.encoding_lookup[key].bytes), self.encoding_lookup[key].bit_pointer, self.encoding_lookup[key].byte_closed)
            decoding_lookup[self.encoding_lookup[key]] = key
            if force_debug:print(decoding_lookup[self.encoding_lookup[key]], self.encoding_lookup[key])
            if force_debug:print()
        self.decoding_lookup = decoding_lookup

    def decode(self, bit_array, prog = False):
        force_debug = False
        time_debug = False

        if force_debug: print(len(bit_array.bytes), bit_array.bit_pointer)

        min_len = min([len(key) for key in self.decoding_lookup.keys()])
        max_len = min(max([len(key) for key in self.decoding_lookup.keys()]), len(bit_array)-1)
        if force_debug: print("minmax", min_len, max_len)
        code_found = True
        output = bytes([])
        if time_debug: seek_time, concat_time = 0, 0

        in_len = len(bit_array)
        if prog: progress = tqdm(total = in_len, desc = "decoding")
        iter = 0
        while iter<in_len and code_found:
            # if force_debug: print(len(bit_array), bytewise_string(output))
            code_found = False
            code = BitArray(bytes([0]),0)
            while len(code) < min_len-1 and iter < in_len:
                if time_debug: concat_time -= time()
                code.append_bit(bit_array.get_bit(iter))
                if time_debug: concat_time += time()
                iter += 1
                if prog: progress.update(1)
            while len(code) <= max_len and iter < in_len:
                if time_debug: seek_time -= time()
                if code in self.decoding_lookup.keys():
                    if time_debug: seek_time += time()
                    output += bytes([self.decoding_lookup[code]])
                    code_found = True
                    # iter += 1
                    break
                elif len(code) < max_len:
                    if time_debug: seek_time += time()
                    if time_debug: concat_time -= time()
                    code.append_bit(bit_array.get_bit(iter))
                    if time_debug: concat_time += time()
                    if prog: progress.update(1)
                    iter += 1
                else:
                    if time_debug: seek_time += time()
                    break
                if force_debug: print(code,iter)
            if not code_found:
                text = "HuffmanTree: unknown bit sequence, unable to decode. Encountered: "+str(code) + " related bytes: " + bytewise_string(bit_array.bytes[(iter-len(code))//8: (iter+1)//8])
                warnings.warn(text)
                break
            #if force_debug: print(code, bit_array)
            #if force_debug: print(bytewise_string(self.decoding_lookup[code]))
            if force_debug: print()
        if time_debug: print("seek", seek_time, "s")
        if time_debug: print("concat", concat_time, "s")
        return output

    def store(self):
        counter = 0
        for key in self.nodes.keys():
            if key>255:
                counter += 1
        output = BitArray(bytearray([counter]), 8)
        for key in self.nodes.keys():
            if key>255:
                node = self.nodes[key]
                coded_node = BitArray(bytearray([
                    node[1]%256,
                    node[1]//256,
                    node[2]%256,
                    node[2]//256
                ]), 8)
                output.self_concat(coded_node)
        # print(output)
        return output