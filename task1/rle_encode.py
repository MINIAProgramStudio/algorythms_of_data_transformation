def bitewise_string(bytes):
    output = ""
    for byte in bytes:
        output += format(byte, '08b') + " "
    return output


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
    return output

def encode_file(source, destination):
    file = None
    try:
        file = open(source, "rb")
        binary = file.read()
        file.close()
    except:
        print("Cant read the source file specified")
        return -1


    try:
        binary = encode(bytes(binary))
    except:
        print("Cant encode the source file specified")
        return -1

    if destination:
        try:
            file = open(destination, "wb")
            file.write(binary)
        except:
            print("Cant write to the file specified")
            return -1
        finally:
            file.close()
    else:
        try:
            file = open(source + ".rle", "wb")
            file.write(binary)
        except:
            print("Cant write to the file specified")
            return -1
        finally:
            file.close()
    return 0


if __name__ == "__main__":
    while True:
        print("Please specify encoding paths.")
        source = input("Source file path:")
        destination = input("Destination path (leave empty for *.rle option):")
        encode_file(source, destination)
