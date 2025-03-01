from BitArray import BitArray, bytewise_string
from BitSequenceFile import BitSequenceFile
from ByteCounter import ByteCounter
from HuffmanTree import HuffmanTree
from time import time

bc = ByteCounter("files/LOR.txt")
ht = HuffmanTree(bc)

read_len = 8

print(ht.encoding_lookup)
print(ht.decoding_lookup)

start = time()
bit_reader = BitSequenceFile("files/LOR.txt")
bit_reader.read(16*8)
text = bit_reader.read(read_len*8)
stop = time()

print("reading", stop-start, "s")

print()
print(text)
print()

start = time()
a = ht.encode(text)
stop = time()

print("encoding", stop-start, "s")

print()
print(a)
print()


start = time()
b = ht.decode(a)
stop = time()

print("decoding", stop-start, "s")

print()
print(BitArray(b, 8))
print()
print("-----")


wrongs = [i for i in range(min(len(b), len(text.bytes))) if b[i] != text.bytes[i]]
wrongs_b = bytes([b[i] for i in wrongs])
wrongs_text = bytes([text.bytes[i] for i in wrongs])
print(read_len, len(text.bytes), len(b), wrongs)


"""
for i in range(len(wrongs)):
    print(wrongs[i])
    print(bytewise_string(wrongs_text[i]))
    code = ht.encode(wrongs_text[i])
    print(code)
    decode = ht.decode(code)
    print(bytewise_string(decode))
    print()

"""