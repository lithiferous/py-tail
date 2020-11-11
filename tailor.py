from io import BytesIO

import argparse
import os
import sys
import time

LINES = 10
SLEEP = 1.0

class TailError(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return self.message

class Tailor:
    def __init__(self, filename, bytes_num, follow, lines_num, sleep_val):
        self.buf       = None
        self.curpos    = None
        self.bytes_num = bytes_num
        self.file      = filename
        self.follow    = follow
        self.lines_num = lines_num
        self.sleep_val = sleep_val
        self.callback  = sys.stdout.buffer.write
        self.tester    = self.check_file(filename)

    def _get_first_byte(self):
        '''finds starting byte by looping back from the EOF'''
        lines = 0
        with open(self.file, 'rb') as f:
            f.seek(-2, 2)
            while True:
                while f.read(1) != b"\n":
                    f.seek(-2, 1)
                lines += 1
                if lines == self.lines_num:
                    break
                f.seek(-2, 1)
            return f.tell()

    def _get_curpos(self):
        '''assigns curpos'''
        if self.bytes_num is not None:
            self.curpos = self.bytes_num
        else:
            self.curpos = self._get_first_byte()

    def _reader(self, f):
        self._get_curpos()
        f.seek(self.curpos)
        return f.read()

    def _reader_buf(self, f):
        self.buf = BytesIO(self._reader(f))
        self.callback(self.buf.read())
        sys.stdout.flush()
        while True:
            mstd = BytesIO(self._reader(f))
            if mstd.getvalue() != self.buf.getvalue():
                self.buf = mstd
                self.callback(self.buf.read())
                sys.stdout.flush()
            time.sleep(self.sleep_val)

    def run(self):
        with open(self.file, 'rb') as f:
            if self.follow:
                self._reader_buf(f)
            else:
                self.callback(self._reader(f))

    def check_file(self, f_):
        ''' Check whether the a given file exists, readable and is a file '''
        if not os.access(f_, os.F_OK):
            raise TailError("File '%s' does not exist" % (f_))
        if not os.access(f_, os.R_OK):
            raise TailError("File '%s' not readable" % (f_))
        if os.path.isdir(f_):
            raise TailError("File '%s' is a directory" % (f_))

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('filenames',
                   type    = str,
                   nargs   = '*')
    p.add_argument('-c',
                   '--bytes',
                   dest    = 'bytes_num',
                   type    = int,
                   default = None,
                   help    = "output starting with a byte NUM of each file")
    p.add_argument('-f',
                   '--follow',
                   dest    = 'follow',
                   action  = 'store_true',
                   help    = "output appended data")
    p.add_argument('-n',
                   '--lines',
                   dest    = "lines_num",
                   type    = int,
                   default = LINES,
                   help    = "output last NUM lines")
    p.add_argument('-s',
                   '--sleep-interval',
                   dest    = "sleep_val",
                   type    = float,
                   default = SLEEP,
                   help    = "with -f option - sleep N seconds before check")
    args = p.parse_args()
    for f in args.filenames:
        Tailor(f, args.bytes_num,
                  args.follow,
                  args.lines_num,
                  args.sleep_val).run()
