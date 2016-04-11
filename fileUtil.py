__author__ = 'jpcla_000'

pointSign = b'.'
numbers = b'0123456789'
zeroSign = b'\x00'
ASCII =  'ASCII'
UTF16 = 'utf-16-le'

def read_in_chunks(file_object, chunk_size=1024000):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data