from BitSequenceFile import BitSequenceFile
from BitArray import BitArray

clean_bit_array = BitArray(open("files/test1.txt","rb").read(), 0)
print(clean_bit_array)

bit_stream = BitSequenceFile("files/test1.txt")
print(bit_stream.read(4))
print(bit_stream.read(16))
