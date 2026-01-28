# 控制量单位：mm/s (0.001m/s) 
# UI中传入数据为m/s，需要进行换算
import math

def moveTobyte(move_list):

    byte_temp = [0x7B,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0xA1,0x7D]
    act_0 = move_list[0]*1000
    act_0 = math.radians(act_0)
    act_1 = move_list[1]*1000
    byte_temp[7],byte_temp[8] = shortTobytes(int(act_0))#航向
    byte_temp[3],byte_temp[4] = shortTobytes(int(act_1))#航速
    byte_check = data_BCC(byte_temp[0:8])
    byte_temp[9] = byte_check
    mes_bytes = ListToBytes(byte_temp)
    print('byte_temp:',byte_temp)
    mes_str = ""
    for i in range(len(byte_temp)):
        mes_str += hex(byte_temp[i]).replace('0x',' ')
    return mes_bytes,mes_str

def forceTobyte(force_list):

    byte_temp = [0x7B,0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0xA1,0x7D]
    act_0 = force_list[0]
    act_1 = force_list[1]
    

    return byte_temp

def data_BCC(list_bytes):
        check_id = None
        for i in range(len(list_bytes)):
            if i :
                check_id ^=(list_bytes[i])
            else:
                check_id = (list_bytes[i])^0
        # print("校验：",check_id)
        # print(type(check_id))
        return check_id

def shortTobytes(short_data):
        """
        转为字节,先返回高8位,再返回低8位
        """
        if short_data >= 0 :
            b_L = short_data & 0xFF
            b_H = short_data >> 8
        else:
            short_data = 0xFFFF - short_data
            b_L = short_data & 0xFF
            b_H = short_data >> 8
        return b_H,b_L

def ListToBytes(mes_list):
     
    Bytes_val = b''
    mes_str = ''
    
    for i in range(len(mes_list)):
        mes_str += '{:02x}'.format(mes_list[i])
        Bytes_val =  bytes.fromhex(mes_str)
    return Bytes_val