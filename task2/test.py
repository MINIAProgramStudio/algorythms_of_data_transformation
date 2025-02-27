from BitSequenceFile import BitSequenceFile, bytewise_string
from BitArray import BitArray
from random import random

read_length = 3
min_step = 1
max_step = 16
a = BitArray(bytes([0b00100101,0b10]),2)
print(a)
for i in range(16):
    a = a<<1
    print(a)