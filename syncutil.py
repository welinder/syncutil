"""
Utilities for syncing and archiving directory trees.
"""
import hashlib

def hexdigest(f, block_size=2**20, fn="md5"):
    """
    Calculates a hex digest on a file in a memory efficient way.
    
    The two most popular hash functions are md5 and sha1. MD5 can be a
    little bit quicker (20%) than SHA1.
    
    Inputs:
    - f: path to a file or a file handle.
    - block_size: [2**20] size of blocks to feed the hash function.
    - fn: ['md5'] hash function to use.
    """
    # stolen from
    # http://stackoverflow.com/questions/1131220/get-md5-hash-of-a-files-without-open-it-in-python
    if type(f) == type(str()):
        f = open(f, 'rb')
    fn = getattr(hashlib, fn)()
    while True:
        data = f.read(block_size)
        if not data:
            break
        fn.update(data)
    return fn.hexdigest()
