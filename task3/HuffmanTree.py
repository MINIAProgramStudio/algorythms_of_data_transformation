from importlib.metadata import Lookup

from BitArray import BitArray, bytewise_string
from ByteCounter import ByteCounter
import copy

class HuffmanTree:
    def __init__(self, byte_counter: ByteCounter):
        self.byte_counter = byte_counter # зберегти
        self.rebuild()

    def rebuild(self, recount = True):
        force_debug = False
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
            else:
                key_a = lowest_keys[0]
                del(opened_nodes[key_a])
                lowest = min(t[0] for t in list(opened_nodes.values()))
                if force_debug: print("e", lowest)
                lowest_keys = [key for key in opened_nodes if opened_nodes[key][0] == lowest]
                if force_debug: print(lowest_keys)
                key_b = lowest_keys[0]
                del (opened_nodes[key_b])
            node_key = 0b100000000 + i
            node_value = self.nodes[key_a][0] + self.nodes[key_b][0]
            self.nodes[node_key] = [node_value, key_a, key_b, None]
            self.nodes[key_a][3] = node_key
            self.nodes[key_b][3] = node_key
            opened_nodes[node_key] = [node_value, key_a, key_b, None]
            if force_debug: print()
        if force_debug: print(self.nodes)
        if force_debug: print(opened_nodes)
        self.root_key = node_key
        self.create_encoding_lookup()
        self.create_decoding_lookup()

    def create_encoding_lookup(self):
        encoding_lookup = {}
        for key in self.nodes:
            if key > 255:
                continue # якщо обраний запис не байт -- нічого не робити
            code = BitArray(bytes([0]), 0)
            selected_key = key
            while True:
                parent_key = self.nodes[selected_key][3]
                if self.nodes[parent_key][1] == selected_key:
                    code = code<<1
                elif self.nodes[parent_key][2] == selected_key:
                    code = code<<1
                    if len(code.bytes) > 1:
                        code.bytes = bytes([code.bytes[0]+1]) + code.bytes[1:]
                    else:
                        code.bytes = bytes([code.bytes[0]+1])
                else:
                    raise Exception("HuffmanTree: node has parent that does not have said node as a child")
                selected_key = parent_key
                if selected_key == self.root_key:
                    break
            encoding_lookup[key] = code
        self.encoding_lookup = encoding_lookup

    def encode(self, object):
        force_debug = False
        if isinstance(object, int):
            if object > 255 or object < 0:
                raise Exception("HuffmanTree can encode only integers 0-255 and bytes")
            return self.encoding_lookup[object]
        elif isinstance(object, bytes):
            output = BitArray([0],0)
            for byte in object:
                code = self.encoding_lookup[byte]
                output = code.concat(output)
            return output
        elif isinstance(object, BitArray):
            output = BitArray([0], 0)
            for byte in object.bytes:
                if force_debug: print("looking for", bytewise_string(byte))
                code = self.encoding_lookup[byte]
                if force_debug: print("code", code)
                output = output.concat(code)
                if force_debug: print("output",output)
                if force_debug: print()
            return output
        else:
            raise Exception("HuffmanTree can encode only integers 0-255 and bytes")

    def create_decoding_lookup(self):
        decoding_lookup = {}
        for key in self.encoding_lookup.keys():
            decoding_lookup[self.encoding_lookup[key]] = key
        self.decoding_lookup = decoding_lookup

    def decode(self, bit_array):
        force_debug = False

        min_len = min([len(key) for key in self.decoding_lookup.keys()])
        max_len = max([len(key) for key in self.decoding_lookup.keys()])
        if force_debug: print("minmax", min_len, max_len)
        code_found = True
        output = bytes([])
        while len(bit_array) and code_found:
            # if force_debug: print(len(bit_array), bytewise_string(output))
            code_found = False
            code_len = min_len
            code = None
            while code_len <= max_len:
                code = bit_array[0:code_len]
                if code in self.decoding_lookup.keys():
                    output += bytes([self.decoding_lookup[code]])
                    code_found = True
                    break
                code_len += 1
                # if force_debug: print(code, code_len, False)
            if not code_found:
                raise Exception("HuffmanTree: unknown bit sequence, unable to decode")
            bit_array = bit_array>>code_len
            if force_debug: print(code, bit_array)
            if force_debug: print(bytewise_string(self.decoding_lookup[code]))
            if force_debug: print()

        return output