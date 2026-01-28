import re

def get_degree():
    '''
    获取多项式的幂与阶数
    :return: 幂，阶数
    '''
    exist_coe = re.findall(r'\*\*(\d+)', poly)
    degree = int(exist_coe[0])
    return degree,exist_coe

def poly_coefficient(degree,exist_coe):
    '''
    根据阶数与幂计算CRC除数
    :param degree:
    :param exist_coe:
    :return: CRC除数
    '''
    coe = []
    for i in range(degree+1):
        coe.append(0)
    for i in range(len(exist_coe)):
        coe[int(exist_coe[i])] = 1
    coe.reverse()
    print('CRC除数:',coe)
    return coe

def supplement_zero(degree,temporary_data):
    '''
    补充原始数据串
    :param degree:
    :return: None
    '''
    for i in range(degree):
        temporary_data.append(0)
    print('补充数据串:',temporary_data)
    return None

def check_summing(coe,temporary_data):
    '''
    计算校验和
    根据CRC除数，生成一组数据
    :return:CRC校验和
    '''
    data_bit = []
    for i in coe:
        data_bit.append(0)
    length = len(data_bit)
    data_bit = temporary_data[:length]
    for i in range(length):
        temporary_data.pop(0)

    reversal = []
    for d in range(len(coe)):
        if coe[d] == 1:
            reversal.append(d)

    while temporary_data!=[]:
        if data_bit[0] == 1:
            for r in reversal[1:]:
                data_bit[r] = 1 if data_bit[r] == 0 else 0
        data_bit.pop(0)
        data_bit.append(temporary_data[0])
        temporary_data.pop(0)
    if data_bit[0] ==1:
        for r in reversal[1:]:
            data_bit[r] = 1 if data_bit[r] == 0 else 0
    data_bit = data_bit[1:]
    print('检验码:',data_bit)
    return data_bit

def check_bit_error(coe,temporary_data):

    '''
    检测数据是否存在误码
    :param coe:
    :param temporary_data:
    :return:None
    '''

    d = temporary_data.copy()
    co = coe.copy()
    while len(temporary_data) > len(coe):
        temporary_i = []
        for c in range(len(coe)):
            if temporary_data[c] == coe[c]:
                temporary_i.append(0)
            else:
                temporary_i.append(1)
        z = 0
        for n in range(len(temporary_i)):
            if temporary_i[n]==1:
                z = n
                break
            z = len(temporary_i)
        temporary_i = temporary_i[z:]
        temporary_data = temporary_i+temporary_data[len(coe):]

    if len(temporary_data)!=len(coe) and temporary_data !=[0] and temporary_data !=[]:
        print('CRC数据:{}----CRC除数:{}传输存在误码'.format(d,co))
    else:
        print('CRC数据:{}----CRC除数:{}不存在误码'.format(d,co))


def run():
    temporary_data = data_string.copy()
    degree,exist_coe = get_degree()
    coe = poly_coefficient(degree,exist_coe)
    supplement_zero(degree,temporary_data)
    data_bit = check_summing(coe,temporary_data)
    answer = data_string + data_bit
    print("最终数据串:",answer)
    check_bit_error(coe,answer)



if __name__ == '__main__':
    # poly = 'x**3+x**2+1'
    data_string = []
    data_input = input('输入二进制数据')
    for i in range(len(data_input)):
        data_string.append(int(data_input[i]))   #将输入的二进制信息码转换成列表
    poly = input('输入生成多项式')
    poly += '*x**0'
    print('数据串:',data_string)
    run()

