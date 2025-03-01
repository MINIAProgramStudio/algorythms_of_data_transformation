from BitArray import BitArray, bytewise_string
from BitSequenceFile import BitSequenceFile
from ByteCounter import ByteCounter
from HuffmanTree import HuffmanTree
from time import time, sleep

file_path = "files/КР2.pdf"

start = time()
bc = ByteCounter(file_path)
bc.count_bytes()
stop = time()
print("counting", stop-start, "s")
sleep(0.5)


ht = HuffmanTree(bc)
sleep(0.5)


read_len = 8

print(ht.encoding_lookup)
print(ht.decoding_lookup)
sleep(0.5)
start = time()
bit_reader = BitSequenceFile(file_path)
#bit_reader.read(159*8)
#text = bit_reader.read(read_len*8)
text = bit_reader.read()
stop = time()
sleep(0.5)

print("reading", stop-start, "s")

"""
print()
print(text)
print(bytewise_string(text.bytes))
print()
"""
start = time()
a = ht.encode(text)
stop = time()
sleep(0.5)

#print("encoding", stop-start, "s")
"""
print()
print(a)

print()
"""

start = time()
b = ht.decode(a)
stop = time()
sleep(0.5)
#print("decoding", stop-start, "s")
"""
print()
print(BitArray(b, 8))
print()
"""
sleep(0.5)
print("-----")


wrongs = [i for i in range(min(len(b), len(text.bytes))) if b[i] != text.bytes[i]]
wrongs_b = bytes([b[i] for i in wrongs])
wrongs_text = bytes([text.bytes[i] for i in wrongs])
print(len(text.bytes), len(a.bytes), len(b), text.bytes == b, len(wrongs))



for i in range(2):
    print(wrongs[i])
    print(bytewise_string(text.bytes[wrongs[i]]))
    print(bytewise_string(b[wrongs[i]]))
    print()
