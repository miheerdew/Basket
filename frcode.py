"""This is a library for the Front compression used by gnu locate.
This library uses the LOCATE02 format.see `man locatedb` for more details """

import struct
from os.path import commonprefix
import six

class CompressionError(Exception):
    pass
    
HEADER=six.b('LOCATE02\0')

def compress( files ,fd ):
    """This function takes a iterator which produces file names,and a \
    file object opened in binary mode for writing.It compresses the filenames\
    using Front Compression( LOCATE02 ) used by gnu locate,and writes them to \
    the file object
    """
    fd.write( struct.pack(   'b%ds'%len(HEADER),
                             0,
                             HEADER
                         )
            )
            
    last_name = ''
    last_offset = 0
    
    for file_name in files:
        offset = len( commonprefix( [file_name,last_name]) )
        rel_offset = offset - last_offset
        last_name = file_name
        last_offset = offset
        rest = six.b(file_name[offset:]) + six.b('\0')
        if  -128<= abs(rel_offset) <= 127:
             data = struct.pack( 'b%ds'%len(rest) ,
                                  rel_offset ,
                                  rest                          
                               ) 
                     
        else:
            data = struct.pack( '>Bh%ds'%len(rest) ,
                                0x80 ,
                                rel_offset ,
                                rest                            
                              )
        fd.write(data)
        
def decompress( fd ):
    """This function takes a fileobject opened in binary mode for reading.
    This data is assumed to be in the LOCATE02 Compressed format.This function
    is a iterator which returns each filename as it iterates.  
    """
    HEAD='b%ds'%len(HEADER)
    
    b,x = struct.unpack( HEAD,
                         fd.read( struct.calcsize( HEAD ) )
                        )
    
    if (b != 0) or (x != HEADER):
        raise CompressionError("Incorrect format")
    
    prev=six.b('')
    offset = 0
    
    while True:
        c = fd.read(1)
        if c == six.b(''):
            break
        
        b = struct.unpack('b',c)[0]
        
        if b == -0x80: # Note I had written 0x80 by mistake
             b = struct.unpack('>h',fd.read(2))[0]
        
        offset = offset + b
        prev = prev[:offset]     
        
        while True:
              c=fd.read(1)
              if c == six.b('\0') or c == six.b(''):
                break
              prev += c 
             
        yield prev
            
if __name__ == '__main__':
        import sys
        if len(sys.argv) > 1:
            six.print_('\n'.join(decompress( sys.stdin )),end='')
        else:
            files=sys.stdin.read().strip().split('\n')
            compress(files,sys.stdout.buffer)
        
