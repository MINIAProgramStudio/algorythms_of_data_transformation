from BitSequenceFile import BitSequenceFile, bytewise_string
from BitArray import BitArray
from random import random

read_length = 3
min_step = 1
max_step = 16
a = BitArray([0],0)
b = BitArray([0],0)
iter = 100
while a.bytes == b.bytes and iter > 0:
    i = read_length * 8
    bit_reader = BitSequenceFile("files/hamlet.txt")
    bit_writer = BitSequenceFile("files/hamlet2.txt", 0)
    read_memory = ""

    while i > 0:
        print("i", i)
        step = int(random()*(max_step-min_step))+min_step
        if step > i: step = i
        bitarray = bit_reader.read(step)
        print(bitarray)
        print()
        read_memory += str(bitarray)
        bit_writer.write(bitarray)
        i -= step
        print()
        print()
    print("i" , i)
    bit_reader.close()
    bit_writer.close()

    bit_reader = BitSequenceFile("files/hamlet.txt")
    a = bit_reader.read(read_length*8)

    bit_reader.close()

    bit_reader = BitSequenceFile("files/hamlet2.txt")
    b = bit_reader.read(read_length*8)

    print(bytewise_string(a.bytes))
    print(read_memory)
    print(bytewise_string(b.bytes))

    bit_reader.close()
    iter -= 1
    print(iter, [a.bytes[i] == b.bytes[i] for i in range(len(b.bytes))])