from BitArray import BitArray, bytewise_string
from ByteCounter import ByteCounter
from BitSequenceFile import BitSequenceFile
import copy
from time import time
from tqdm import tqdm
from HuffmanTree import HuffmanTree


def huffman_encode(path_from, path_to = None, chunk = 256):
    if path_to is None or not path_to:
        path_to = path_from + ".huff"
    bc = ByteCounter(path_from)
    bc.count_bytes()
    ht = HuffmanTree(bc)
    #print(ht.nodes)
    bit_reader = BitSequenceFile(path_from)
    bit_writer = BitSequenceFile(path_to, 0)

    bit_writer.write(ht.store()) # записуємо розгалуження дерева в початок файла
    read = bit_reader.read(chunk*8) # читаємо чанк байтів, кодуємо його та записуємо у файл
    progress = tqdm(total = bit_reader.file_length, desc = "encoding")
    for i in range(bit_reader.file_length//chunk + ((bit_reader.file_length%chunk)>1)):
        progress.update(chunk)
        bit_writer.write(ht.encode(read))
        read = bit_reader.read(chunk*8)
    bit_writer.file.write(bytes([
        bit_writer.bit_pointer
    ]))
    bit_writer.close() # закриваємо файли
    bit_reader.close()

def huffman_decode(path_from, path_to = None, chunk = 1024):
    if (path_to is None or not path_to) and path_from[-5:] == ".huff":
        path_to = path_from[:-5]
    ht = HuffmanTree(None)

    bit_reader = BitSequenceFile(path_from)
    destination = open(path_to, "wb")

    #визначаємо кількість розгалужень
    bit_array = bit_reader.read(8)
    forks = bit_array.bytes[0]
    #print(forks)

    fork_nodes = {}
    #записуємо розгалуження
    for iter in range(forks):
        bit_array = bit_reader.read(32)
        left = bit_array.bytes[0] + ((bit_array.bytes[1]&1)*256)
        right = bit_array.bytes[2] + ((bit_array.bytes[3]&1)*256)
        fork_nodes[256+iter] = [None, left, right, None]
        ht.nodes[256+iter] = [None, left, right, None]
    #print(fork_nodes)

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
    #print(ht.nodes)

    # шукаємо корінь
    for key in ht.nodes.keys():
        if ht.nodes[key][3] is None:
            ht.root_key = key
            break

    #збираємо дерево
    ht.create_encoding_lookup()
    ht.create_decoding_lookup()
    #print(ht.decoding_lookup)

    #декодуємо
    huff = bit_reader.read()
    bit_pointer = int(huff.bytes[-1])
    #print(bit_pointer)
    huff.bytes = huff.bytes[:-1]
    huff.bit_pointer = bit_pointer
    if bit_pointer:
        huff.byte_closed = False
    #print(len(huff))
    destination.write(ht.decode(huff, True))