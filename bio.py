def bytesToShort(bytes_data):
        a1 = bytes_data[0] << 8 | bytes_data[1]
        if a1 & 0x8000 == 0x8000 :
            b = 0xFFFF - a1
            return b
        else:
            return a1

byte_temp = b'\x7B\x00\x00\x00\x01\x00\x00\x00\x00\xA1\x7D'
num_val = 0xFF
num_hex = b''
num_list = [0x7B,0x00,0x00,0x01,0x01,0x01,0x01,0xFF,0xA1,0xA1,0x7D]
for i in range(len(num_list)):
    num_hex += chr(num_list[i]).encode("utf-8")
hex_val = chr(num_val)
print(num_val)
print(type(num_val))
print(hex_val.encode("utf-8"))
print(num_hex)

print(bytesToShort(num_hex[6:8]))

# print(byte_temp)
# .write(chr(0x06).encode("utf-8"))

