#coding=utf-8
import os,codecs,struct,sys
from cStringIO import StringIO
from bcfnt_plugin import bcfnt_info
def bits(byte):
    return ((byte >> 7) & 1,\
            (byte >> 6) & 1,\
            (byte >> 5) & 1,\
            (byte >> 4) & 1,\
            (byte >> 3) & 1,\
            (byte >> 2) & 1,\
            (byte >> 1) & 1,\
            (byte) & 1)
def dir_fn(adr):
    dirlst=[]
    for root,dirs,files in os.walk(adr):
        for name in files:
            adrlist=os.path.join(root, name)
            dirlst.append(adrlist)
    return dirlst
def get_darc_info(fn):
    fp = open(fn ,'rb')
    magic = fp.read(4)
    if magic != 'darc':
        fp.close()
        return [] , {} , []
    endian_type , index_block_offset = struct.unpack('2H',fp.read(4))
    endian = '<'
    if endian_type != 0xfeff:
        endian = '>'
    version , arc_file_size ,table_offset, table_size , data_offset = struct.unpack('%s5I'%endian,fp.read(0x14))
    nums = 1
    fp.seek(index_block_offset)
    (filename_offset , file_offset , file_length) = struct.unpack('%s3I'%endian,fp.read(0xc))
    folder_mark = bits(filename_offset >> 24)[7]
    
    if folder_mark:
        #if folder
        nums = file_length
    name_table_offset = nums * 0xc + 0x1c
    fp.seek(index_block_offset)
    file_block_list = []
    file_info_dict = {}
    pos = index_block_offset
    base_folder_name = ''
    package_info = []
    package_info.append((endian , index_block_offset , arc_file_size ,data_offset ,nums) )  
    for i in xrange(nums):
        fp.seek(pos)
        (filename_offset , file_offset , file_length) = struct.unpack('%s3I'%endian,fp.read(0xc))
        
        folder_mark = bits(filename_offset >> 24)[7]
        filename_offset = name_table_offset + filename_offset % 0x10000
        fp.seek(filename_offset)
        mems = StringIO()
        firstByte , secondByte = 1, 1
        while ((firstByte,secondByte) != (0,0)):
            firstByte = ord(fp.read(1))
            secondByte = ord(fp.read(1))
            if (firstByte,secondByte) != (0,0):
                mems.write(chr(firstByte) + chr(secondByte))
        name_data = mems.getvalue()
        filename = name_data.decode('utf-16')
        mems.flush()
        if folder_mark:
            base_folder_name = filename
        else:
            file_block_list.append((pos , file_offset , file_length , base_folder_name ,filename ))
            #print(u'%s > %s :[index_offset:%08x , file_offset:%08x , file_length:%08x]'%(base_folder_name ,filename , \
            #                                                                            pos , file_offset , file_length))
            if base_folder_name == '.':
                dest_file_name = r'\%s'%(filename)
            else:
                dest_file_name = r'\%s\%s'%(base_folder_name , filename)
            file_info_dict[dest_file_name] = (pos , file_offset , file_length)
        pos += 0xc
    fp.close()
    return file_block_list , file_info_dict , package_info
def checkFont(fn):
    char_map_list = bcfnt_info(fn)
    b = '.'.join(char_map_list)
    print(b)
    try:
        b.encode('ascii')
        return True
    except:
        return False
def getFontSize(fn):
    if '_' in fn:
        font_size = fn.split('.')[0].split('_')[-1]
        return font_size
    return None
def unpack_darc(fn):
    file_block_list , file_info_dict , package_info = get_darc_info(fn)
    if len(package_info) > 0:
        print(u'PACKAGE NAME :%s \n'%fn.decode('cp936') + \
              u'FILE NUMS :%d \n'%package_info[0][4] + \
              u'TALBE OFFSET :%08x \n'%package_info[0][1] + \
              u'PACKAGE SIZE :%08x \n'%package_info[0][2] + \
              u'DATA OFFSET :%08x \n'%package_info[0][3])
        fp = open(fn , 'rb')
        for (pos , file_offset , file_length , base_folder_name ,filename ) in file_block_list:
            if not os.path.isdir(u'%s_unpacked\\%s'%(fn.decode('cp936') , base_folder_name)):
                os.makedirs(u'%s_unpacked\\%s'%(fn.decode('cp936') , base_folder_name))
            dest = open(u'%s_unpacked\\%s\\%s'%(fn.decode('cp936') , base_folder_name , filename),'wb')
            fp.seek(file_offset)
            data = fp.read(file_length)
            dest.write(data)
            dest.close()
        fp.close()
    else:
        print(u'PACKAGE NAME :%s \n'%fn.decode('cp936') + \
              u'NOT A NINTENDO DARC')

    pass

def pack_darc(fn):
    align_ext = ['bcfnt' , 'bclim']#对这些类型的文件使用文件对齐
    file_block_list , file_info_dict , package_info = get_darc_info(fn)
    if len(package_info) > 0:
        print(u'PACKAGE NAME :%s \n'%fn.decode('cp936') + \
              u'FILE NUMS :%d \n'%package_info[0][4] + \
              u'TALBE OFFSET :%08x \n'%package_info[0][1] + \
              u'PACKAGE SIZE :%08x \n'%package_info[0][2] + \
              u'DATA OFFSET :%08x \n'%package_info[0][3])
    fp = open(fn , 'rb+')
    unpacked_folder_name = u'%s_unpacked'%(fn.decode('cp936'))
    if not os.path.isdir(u'%s_unpacked'%(fn.decode('cp936'))):
        print(u'缺少打包文件夹，请把要打包的文件放入同名文件夹中')
        os.makedirs(u'%s_unpacked'%(fn.decode('cp936')))
    fl = dir_fn(unpacked_folder_name)
    f_pos = package_info[0][3]
    fp.seek(f_pos)
    fp.truncate()
    for item in file_block_list:
        (pos , file_offset , file_length , base_folder_name ,filename ) = item
        if base_folder_name == '.':
            real_file_name = r'%s\%s'%(unpacked_folder_name , filename)
        else:
            real_file_name = r'%s\%s\%s'%(unpacked_folder_name , base_folder_name , filename)
        fd = open(real_file_name , 'rb')
        #print('%s'%real_file_name)
        n_data = fd.read()
        fd.close()
        fp.seek(f_pos)
        ext_name =  real_file_name.split('.')[-1].lower()
        if '_' in filename and '.bcfnt' in filename:
            font_size = getFontSize(filename)
            cfont_name = 'chs_font//%s.bcfnt'%font_size
            #cfont_name = 'chs_font//%s'%filename
            if os.path.exists(cfont_name)  and checkFont(real_file_name)==False:
                print('match font size :using:%s'%cfont_name)
                fd = open(cfont_name , 'rb')
                n_data = fd.read()
                fd.close()
        if ext_name in align_ext:
            align = 0x80 - f_pos%0x80
            fp.write('\x00' * align)
            f_pos += align
            fp.seek(f_pos)
        file_offset = fp.tell()
        file_length = len(n_data)
        fp.write(n_data)
        f_pos = fp.tell()
        fp.seek(pos + 4 , 0)
        fp.write(struct.pack('I' , file_offset))
        fp.write(struct.pack('I' , len(n_data)))
        #print('pack to >>>> %08x'%file_offset)
    fp.seek(0,2)
    end_pos = fp.tell()
    fp.seek(0xc ,0)
    fp.write(struct.pack('I' , end_pos))
    fp.close()
    pass
        
        
        
        
        
            
def inject_darc(fn):
    file_block_list , file_info_dict , package_info = get_darc_info(fn)
    if len(package_info) > 0:
        print(u'PACKAGE NAME :%s \n'%fn.decode('cp936') + \
              u'FILE NUMS :%d \n'%package_info[0][4] + \
              u'TALBE OFFSET :%08x \n'%package_info[0][1] + \
              u'PACKAGE SIZE :%08x \n'%package_info[0][2] + \
              u'DATA OFFSET :%08x \n'%package_info[0][3])
    fp = open(fn , 'rb+')
    unpacked_folder_name = u'%s_unpacked'%(fn.decode('cp936'))
    if not os.path.isdir(u'%s_unpacked'%(fn.decode('cp936'))):
        print(u'缺少注入文件夹，请把要注入的文件放入同名文件夹中')
        os.makedirs(u'%s_unpacked'%(fn.decode('cp936')))
    
    fl = dir_fn(unpacked_folder_name)
    for dest_name in fl:
        n_value = dest_name.split(unpacked_folder_name)[1]
        if n_value in file_info_dict:
            print('%s'%n_value)
            (pos , file_offset , file_length) = file_info_dict[n_value]
            fd = open(dest_name , 'rb')
            n_data = fd.read()
            fd.close()
            filename = n_value
            if '_' in filename and '.bcfnt' in filename:
                font_size = getFontSize(filename)
                cfont_name = 'chs_font//%s.bcfnt'%font_size
                #cfont_name = 'chs_font//%s'%filename
                if os.path.exists(cfont_name) and checkFont(real_file_name)==False:
                    print('match font size :using:%s'%cfont_name)
                    fd = open(cfont_name , 'rb')
                    n_data = fd.read()
                    fd.close()
            if len(n_data) <= file_length:
                #print('INJECT in >>>> %08x'%file_offset)
                fp.seek(file_offset)
                fp.write(n_data)
                fp.write('\x00' * (file_length - len(n_data)))
                fp.seek(pos + 4 , 0)
                fp.write(struct.pack('I' , file_offset))
                fp.write(struct.pack('I' , len(n_data)))
            else:
                real_file_name = n_value
                
                fp.seek(0,2)
                ext_name =  real_file_name.split('.')[-1].lower()
                if ext_name in align_ext:
                    f_pos = fp.tell()
                    align = 0x80 - f_pos%0x80
                    fp.write('\x00' * align)
                file_offset = fp.tell()
                #print('EXTEND to >>>> %08x'%file_offset)
                fp.write(n_data)
                fp.seek(pos + 4 , 0)
                fp.write(struct.pack('I' , file_offset))
                fp.write(struct.pack('I' , len(n_data)))
    fp.seek(0,2)
    end_pos = fp.tell()
    fp.seek(0xc ,0)
    fp.write(struct.pack('I' , end_pos))
    fp.close()
            
            
    pass
def test():
    flag = sys.argv
    if len(flag)<=2:
        flag.append('')
        print('usage :\n' +\
              'unpack darc files : DARC_tool -unpack 123.arc \n' +\
              'inject darc files : DARC_tool -pack 123.arc \n')
    elif len(flag)>2 and flag[1] == '-unpack':
        fn = flag[2]
        unpack_darc(fn)
    elif len(flag)>2 and flag[1] == '-inject':
        fn = flag[2]
        inject_darc(fn)
    elif len(flag)>2 and flag[1] == '-pack':
        fn = flag[2]
        pack_darc(fn)
    else:
        print('usage :\n' +\
              'unpack darc files : DARC_tool -unpack 123.arc \n' +\
              'inject darc files : DARC_tool -inject 123.arc \n' +\
              'repack darc files : DARC_tool -pack 123.arc \n')
def main():
    test()
if __name__ == '__main__':
    main()

    
    
        
        
    
