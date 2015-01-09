import struct , codecs
def bcfnt_info(name):
    fp = open(name , 'rb')
    magic = fp.read(4)
    char_map_list = []
    if magic == 'CFNT':
        fp.seek(0xc)
        file_size ,  = struct.unpack('I' , fp.read(4))
        i = 0x14
        fp.seek(0x14)
        
        while i < file_size:
            fp.seek(i)
            magic = fp.read(4)
            if magic == 'FINF':
                size, = struct.unpack('I' , fp.read(4))
                fp.seek(size - 4 , 1)
                i += size
                pass
            if magic == 'TGLP':
                size, = struct.unpack('I' , fp.read(4))
                fp.seek(size - 4 , 1)
                i += size
                pass
            if magic == 'CWDH':
                size, = struct.unpack('I' , fp.read(4))
                fp.seek(size - 4 , 1)
                i += size
                pass
            if magic == 'CMAP':
                size, = struct.unpack('I' , fp.read(4))
                a ,b , c = struct.unpack('3H' , fp.read(6))
                fp.seek(6 , 1)
                if (a ,b ,c) == (0 ,0xffff , 2):
                    nums, = struct.unpack('H' , fp.read(2))
                    for n in xrange(nums):
                        unicode_id , char_index_id = struct.unpack('2H' , fp.read(4))
                        if 0x3000  <=unicode_id <= 0XFFA0:
                            char = struct.pack('H' , unicode_id).decode('UTF-16')
                            char_map_list.append(char)
                i += size
                pass
            else:
                i += 4
    return char_map_list

