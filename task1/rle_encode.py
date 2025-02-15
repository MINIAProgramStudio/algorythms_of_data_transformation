from itertools import count


def encode(in_bytes):
    output = bytes()
    bufer = bytes()
    #print(bufer, len(bufer), output)
    for byte in in_bytes:

        if len(bufer) > 127:
            if bufer[-1] == bufer[-2]:
                if len(bufer) == 129:
                    # переповнення послідовності однакових байтів
                    output += bytes([255])
                    output += bytes([bufer[0]])
                    bufer = bytes()
            else:
                # переповнення послідовності різних байтів
                output += bytes([127])
                output += bufer
                bufer = bytes()
        if len(bufer)>1:
            if bufer[-1] == byte:
                if bufer[-2] != byte:
                    # закінчено послідовність різних байтів
                    output += bytes([len(bufer)-1])
                    output += bufer
                    bufer = bytes()
            else:
                if bufer[-1]==bufer[-2]:
                    # закінчено послідовність однакових байтів
                    output += bytes([126 + len(bufer)])
                    output += bytes([bufer[0]])
                    bufer = bytes()
        bufer = bufer + bytes([byte])
    if len(bufer) > 1:
        if bufer[-1] == bufer[-2]:
            # закінчено послідовність однакових байтів
            output += bytes([126 + len(bufer)])
            output += bytes([bufer[0]])
        else:
            # закінчено послідовність різних байтів
            output += bytes([len(bufer) - 1])
            output += bufer
            bufer = bytes()
    elif len(bufer) > 0:
        # закінчено послідовність різних байтів
        output += bytes([len(bufer) - 1])
        output += bufer
        bufer = bytes()



        #print(bufer, len(bufer), output)
    return output