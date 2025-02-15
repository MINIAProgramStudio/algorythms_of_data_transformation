def decode(in_bytes):
    output = bytes()
    pointer = 0
    while pointer < len(in_bytes):
        if in_bytes[pointer]>127:
            # повторення байту
            output += bytes([in_bytes[pointer+1]]*(in_bytes[pointer]-126))
            pointer += 2
        else:
            # переписування байтів
            output += bytes(in_bytes[pointer + 1:pointer+ 1 + in_bytes[pointer]])
            pointer += in_bytes[pointer]
    return output