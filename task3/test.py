from BitArray import BitArray, bytewise_string
from BitSequenceFile import BitSequenceFile
from ByteCounter import ByteCounter
from HuffmanTree import HuffmanTree
from time import time, sleep
from HuffmanFileCoder import huffman_encode, huffman_decode
import os
from PythonTableConsole import PythonTableConsole
import filecmp

raw_folder = "files/raw"
encoded_folder = "files/encoded"
decoded_folder = "files/decoded"
log_path = "files/test_log.txt"

raw_files = os.listdir(raw_folder)

table = ["name", "raw length, KB", "encoded length, KB", "compression, %", "time to encode, s", "time to decode, s", "all correct"]

for file in raw_files:
    print(file)
    raw_path = raw_folder + "/" + file
    encoded_path = encoded_folder + "/" + file + ".huff"
    decoded_path = decoded_folder + "/" + file

    time_to_encode = -time()
    huffman_encode(raw_path, encoded_path)
    time_to_encode += time()

    time_to_decode = -time()
    huffman_decode(encoded_path, decoded_path)
    time_to_decode += time()

    table.append([
        file,
        os.path.getsize(raw_path)//1024,
        os.path.getsize(encoded_path)//1024,
        round(os.path.getsize(encoded_path)*100 / os.path.getsize(encoded_path),1),
        time_to_encode,
        time_to_decode,
        filecmp.cmp(raw_path, encoded_path)
    ])
    sleep(0.5)

table = PythonTableConsole(table)
table.transpose()
print(table)