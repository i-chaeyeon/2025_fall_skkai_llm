def unicode1():
    chr(0)
    print(chr(0))
    "this is a test" + chr(0) + "string"
    print("this is a test" + chr(0) + "string")

def unicode2():
    test_string = "hello! 안녕하세요!"
    utf8_encoded = test_string.encode("utf-8")
    utf16_encoded = test_string.encode("utf-16")
    utf32_encoded = test_string.encode("utf-32")
    print(utf8_encoded)  ## b'hello! \xec\x95\x88\xeb\x85\x95\xed\x95\x98\xec\x84\xb8\xec\x9a\x94!'
    print(utf16_encoded) ## b'\xff\xfeh\x00e\x00l\x00l\x00o\x00!\x00 \x00H\xc5U\xb1X\xd58\xc1\x94\xc6!\x00'
    print(utf32_encoded) ## b'\xff\xfe\x00\x00h\x00\x00\x00e\x00\x00\x00l\x00\x00\x00l\x00\x00\x00o\x00\x00\x00!\x00\x00\x00 \x00\x00\x00H\xc5\x00\x00U\xb1\x00\x00X\xd5\x00\x008\xc1\x00\x00\x94\xc6\x00\x00!\x00\x00\x00'
    print(type(utf8_encoded)) ## <class 'bytes'>

    ## Get the byte values for the encoded string (integers from 0 to 255)
    print(list(utf8_encoded)) ## [104, 101, 108, 108, 111, 33, 32, 236, 149, 136, 235, 133, 149, 237, 149, 152, 236, 132, 184, 236, 154, 148, 33]
    
    ## One byte does not necessarily correspond to one Unicode character
    print(len(test_string))
    print(len(utf8_encoded))

    ## decode
    print(utf8_encoded.decode("utf-8"))

def decode_utf8_bytes_to_str_wrong(bytestring: bytes):
    return "".join([bytes([b]).decode("utf-8") for b in bytestring])


print(decode_utf8_bytes_to_str_wrong("이".encode("utf-8")))