from rle_encode import encode
from rle_decode import decode

text = "AAAAAA"
encoding = "UTF-8"

def bitewise_string(bytes):
    output = ""
    for byte in bytes:
        output += format(byte, '08b') + " "
    return output

print(bitewise_string(bytes(text, encoding)))
print(bitewise_string(encode(bytes(text, encoding))))
print(bitewise_string(decode(encode(bytes(text, encoding)))))