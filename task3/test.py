from BitArray import BitArray
from BitSequenceFile import BitSequenceFile
from ByteCounter import ByteCounter
from HuffmanTree import HuffmanTree

bc = ByteCounter("files/hamlet.txt")
ht = HuffmanTree(bc)

bit_reader = BitSequenceFile("files/hamlet.txt")
print(ht.encode(bit_reader.read(64)))