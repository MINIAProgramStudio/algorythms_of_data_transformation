from BitArray import BitArray, bytewise_string
from BitSequenceFile import BitSequenceFile
from ByteCounter import ByteCounter
from HuffmanTree import HuffmanTree

bc = ByteCounter("files/hamlet.txt")
ht = HuffmanTree(bc)

bit_reader = BitSequenceFile("files/hamlet.txt")
text = bit_reader.read(40)
print(bytewise_string(text.bytes))

a = ht.encode(text)
print(bytewise_string(a.bytes))

b = ht.decode(a)
print(bytewise_string(b))