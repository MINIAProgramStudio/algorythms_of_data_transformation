from BitSequenceFile import BitSequenceFile, bytewise_string
from BitArray import BitArray
from random import random

print("len(BitArray(bytes([0b1010]), 4))",len(BitArray(bytes([0b1010]), 4)))
print("str(BitArray(bytes([0b1010]), 4) >> 1)", str(BitArray(bytes([0b1010]), 4) >> 1))
print("str(BitArray(bytes([0b1010]), 4) << 1)", str(BitArray(bytes([0b1010]), 4) << 1))
print("BitSequenceFile('files/hamlet.txt').read(4)", BitSequenceFile("files/hamlet.txt").read(8))

min_len = 1
max_len = 1024
read_len = 1024

bit_reader = BitSequenceFile("files/hamlet.txt")
bit_writer = BitSequenceFile("files/hamlet2.txt", 0)
iter = read_len*8
while iter > 0:
    step = int(random()*(max_len-min_len)) + min_len
    if step>iter: step = iter
    bit_array = bit_reader.read(step)
    bit_writer.write(bit_array)
    iter-=step
bit_reader.close()
bit_writer.close()
