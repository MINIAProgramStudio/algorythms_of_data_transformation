from BitArray import BitArray, bytewise_string
from BitSequenceFile import BitSequenceFile
from ByteCounter import ByteCounter
from HuffmanTree import HuffmanTree
from time import time
from HuffmanFileCoder import huffman_encode, huffman_decode

source = "files/LOR.txt"

huffman_encode(source)
huffman_decode(source + ".huff")
