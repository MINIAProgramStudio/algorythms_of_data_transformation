from BitSequenceFile import BitSequenceFile
from BitArray import BitArray
from random import random

read_length = 4
min_step = 9
max_step = 9
a = BitArray([0],0)
b = BitArray([0],0)
iter = 10
while a.bytes == b.bytes and iter > 0:
    i = read_length * 8
    bit_reader = BitSequenceFile("files/hamlet.txt")
    bit_writer = BitSequenceFile("files/hamlet2.txt", 0)
    while i > 0:
        print("i", i)
        step = int(random()*(max_step-min_step))+min_step
        if step > i: step = i
        bitarray = bit_reader.read(step)
        print(bitarray)

        bit_writer.write(bitarray)
        i -= step
        print()
    print("i" , i)
    bit_reader.close()
    bit_writer.close()

    bit_reader = BitSequenceFile("files/hamlet.txt")
    a = bit_reader.read(read_length*8)
    print(a)
    bit_reader.close()

    bit_reader = BitSequenceFile("files/hamlet2.txt")
    b = bit_reader.read(read_length*8)
    print(b)
    bit_reader.close()
    iter -= 1
    print(iter, [a.bytes[i] == b.bytes[i] for i in range(len(a.bytes))])