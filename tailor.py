from multiprocessing import Pool

import argparse
import os
import sys
import time

CPUS  = 4
LINES = 10
SLEEP = 1.0

class TailError(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return self.message

class Tailor:
    def __init__(self, filename, bytes_num, follow, lines_num, sleep_val):
        self.file      = filename
        self.bytes_num = bytes_num
        self.follow    = follow
        self.lines_num = lines_num
        self.sleep_val = sleep_val
        self.curpos    = None
        self.callback  = sys.stdout.write
        self.tester    = self.check_file_validity(filename)

    def _get_line_pos(self):
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
            self.curpos = self._get_line_pos()

    def _reader(self, f):
        self._get_curpos()
        f.seek(self.curpos)
        lines = f.readlines()
        self.callback("".join(l.decode('utf-8') for l in lines))

    def run(self):
        with open(self.file, 'rb') as f:
            if self.follow:
                while True:
                    self._reader(f)
                    time.sleep(self.sleep_val)
            else:
                self._reader(f)

    def check_file_validity(self, file_):
        ''' Check whether the a given file exists, readable and is a file '''
        if not os.access(file_, os.F_OK):
            raise TailError("File '%s' does not exist" % (file_))
        if not os.access(file_, os.R_OK):
            raise TailError("File '%s' not readable" % (file_))
        if os.path.isdir(file_):
            raise TailError("File '%s' is a directory" % (file_))


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
    for f in args.filenames:
        Tailor(f, args.bytes_num,
                  args.follow,
                  args.lines_num,
                  args.sleep_val).run()

#def process(files):
#    '''Maps tail process to multiplecores'''
#    for f in files:
#        Tailor(f, args.bytes_num,
#                  args.follow,
#                  args.lines_num,
#                  args.sleep_val).run()
#    args = p.parse_args()
#    print(args)
#    pool = Pool(processes=CPUS)
#    with pool as p:
#        p.map(process, args.filenames)
#

