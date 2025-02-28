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

    def encode(self, byte):
        pass


