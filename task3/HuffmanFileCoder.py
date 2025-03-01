from BitArray import BitArray, bytewise_string
from ByteCounter import ByteCounter
from BitSequenceFile import BitSequenceFile
import copy
from time import time
from tqdm import tqdm
from HuffmanTree import HuffmanTree


def huffman_encode(path_from, path_to = None, chunk = 1024):
    if path_to is None:
        path_to = path_from + ".huff"
    bc = ByteCounter(path_from)
    ht = HuffmanTree(bc)
    bit_reader = BitSequenceFile(path_from)
    bit_writer = BitSequenceFile(path_to, 0)

    bit_writer.write(ht.store()) # записуємо розгалуження дерева в початок файла

    read = bit_reader.read(chunk*8) # читаємо чанк байтів, кодуємо його та записуємо у файл
    progress = tqdm(total = bit_reader.file_length, desc = "encoding")
    while len(read.bytes)>1 or read.bit_pointer != 0:
        progress.update(chunk)
        bit_writer.write(ht.encode(read))
        read = bit_reader.read(chunk*8)
    bit_writer.close() # закриваємо файли
    bit_reader.close()

def huffman_decode(path_from, path_to = None):
    if path_to is None and path_from[-5:] == ".huff":
        path_to = path_from[:-5]
    ht = HuffmanTree(None)
    bit_reader = BitSequenceFile(path_from)
    bit_writer = BitSequenceFile(path_to, 0)

    #визначаємо кількість розгалужень
    bit_array = bit_reader.read(9)
    forks = bit_array.bytes[0] + bit_array.bytes[1]*256

    fork_nodes = {}
    #записуємо розгалуження
    for iter in range(forks):
        bit_array = bit_reader.read(9)
        left = bit_array.bytes[0] + bit_array.bytes[1]*256
        bit_array = bit_reader.read(9)
        right = bit_array.bytes[0] + bit_array.bytes[1] * 256
        fork_nodes[255+iter] = [None, left, right, None]
        ht.nodes[255+iter] = [None, left, right, None]

    #прописуємо батьків розгалуженням та додаємо записи для байтів
    for key in fork_nodes.keys():
        left = fork_nodes[key][1]
        right = fork_nodes[key][2]
        if left in ht.nodes.keys():
            ht.nodes[left][3] = key
        else:
            ht.nodes[left] = [None, None, None, key]
        if right in ht.nodes.keys():
            ht.nodes[right][3] = key
        else:
            ht.nodes[right] = [None, None, None, key]

    #збираємо дерево
    ht.create_encoding_lookup()
    ht.create_decoding_lookup()

    #декодуємо
    bit_writer.write(ht.decode(bit_reader.read()))