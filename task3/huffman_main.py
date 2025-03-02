from HuffmanFileCoder import huffman_encode, huffman_decode

if __name__ == "__main__":
    while True:
        text = ""
        try:
            text = input()
        except:
            print("Input failure")
            continue
        if len(text) < 6:
            print("Invalid command")
            continue

        if text[:6] == "encode":
            text = text[7:]
            if not ";" in text:
                print("no ; found between source and destination. Even if destination is empty ; is required")
                continue
            huffman_encode(text[:text.index(";")],text[text.index(";")+1:])
            print("encoded")
            continue
        elif text[:6] == "decode":
            text = text[7:]
            if not ";" in text:
                print("no ; found between source and destination. Even if destination is empty ; is required")
                continue
            huffman_decode(text[:text.index(";")],text[text.index(";")+1:])
            print("decoded")
            continue
        else:
            print("unknown command")
            continue

