def bitewise_string(bytes):
    output = ""
    for byte in bytes:
        output += format(byte, '08b') + " "
    return output

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

            output += bytes(in_bytes[pointer + 1:pointer +2+ in_bytes[pointer]])
            pointer += in_bytes[pointer]+2

    return output

def decode_file(source, destination):
    file = None
    try:
        file = open(source, "rb")
        binary = file.read()
        file.close()
    except:
        print("Cant read the source file specified")
        return -1


    try:
        binary = decode(bytes(binary))
    except:
        print("Cant decode the source file specified")
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
            file = open(source[:-4], "wb")
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
        decode_file(source, destination)
