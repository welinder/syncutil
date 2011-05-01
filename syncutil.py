"""
Utilities for syncing and archiving directory trees.
"""
import hashlib, os, re
from os.path import exists, join, relpath
import ctypes as ct

def hexdigest(f, blocksize=2**20, fn="md5"):
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
        data = f.read(blocksize)
        if not data:
            break
        fn.update(data)
    return fn.hexdigest()

excludeTypes = [
    ".svn",
    ".git" ]
excludePatterns = [
    "\.svn",
    ".*\.pyc",
    ".*\.o",
    ".*\.a",
    ".*~",
    "\.#.*",
    "\.DS_Store"]

def index_tree(root, f, exptrn=None, exdirs=None, expath=None):
    """
    Indexes all files in a directory tree to a text file. One file per line.

    Inputs:
    - root: the root path to start indexing at.
    - f: filename of file handle to an output text file.
    - exptrn: list of regex patterns to exclude (will be enclosed in ^$).
    - exdirs: ['.svn', '.git'] directory types to exclude.
    - expath: list of paths (relative to root) to exclude.
    """
    if type(f) == type(str()):
        f = open(f, "wt")
    excludePattern = "|".join(map(lambda s: "^%s$" % s,
                                  excludePatterns + (exptrn or [])))
    excludeDirs = excludeTypes + (exdirs or [])
    root = os.path.abspath(root)
    for dirpath, dirs, files in os.walk(root):
        # write files to output
        for filename in files:
            if re.search(excludePattern, filename): continue
            f.write(join(dirpath, filename) + "\n")
        # exclude certain directory patterns or types
        for dname in list(dirs):
            print join(dirpath, dname)
            if re.search(excludePattern, dname) \
                   or any([exists(join(dirpath, dname, tname)) \
                           for tname in excludeDirs]) \
                   or relpath(join(dirpath, dname), root) in (expath or []):
                dirs.remove(dname)

class struct_timespec(ct.Structure):
    _fields_ = [('tv_sec', ct.c_long), ('tv_nsec', ct.c_long)]

class struct_stat64(ct.Structure):
    _fields_ = [
        ('st_dev', ct.c_int32),
        ('st_mode', ct.c_uint16),
        ('st_nlink', ct.c_uint16),
        ('st_ino', ct.c_uint64),
        ('st_uid', ct.c_uint32),
        ('st_gid', ct.c_uint32), 
        ('st_rdev', ct.c_int32),
        ('st_atimespec', struct_timespec),
        ('st_mtimespec', struct_timespec),
        ('st_ctimespec', struct_timespec),
        ('st_birthtimespec', struct_timespec),
        ('dont_care', ct.c_uint64 * 8)
    ]

libc = ct.CDLL('libc.dylib')
stat64 = libc.stat64
stat64.argtypes = [ct.c_char_p, ct.POINTER(struct_stat64)]

def get_creation_time(path):
    """
    Return the creation time of a file.
    """
    buf = struct_stat64()
    rv = stat64(path, ct.pointer(buf))
    if rv != 0:
        raise OSError("Couldn't stat file %r" % path)
    return buf.st_birthtimespec.tv_sec
