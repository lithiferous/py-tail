import argparse
import os
import sys
import time

LINES = 10
SLEEP = 1.0


class Tailor:
    def __init__(self, bytes_num, file, follow, lines_num, sleep_val):
        self.bytes_num = bytes_num
        self.file      = file
        self.follow    = follow
        self.lines_num = lines_num
        self.sleep_val = sleep_val
        self.curpos    = self._get_curpos()
        self.callback  = sys.stdout.write

    def run(self):
        with open(self.file) as f:
            if (self.follow):
                while True:
                    _reader(self, f)
            else:
                _reader(self, f)

    def _get_line_pos(self):
        '''finds starting byte by looping back from the EOF'''
        lines = 0
        self.file.seek(-2, 2)
        while lines != self.lines_num:
            while f.read(1) != b"\n":
                self.file.seek(-2, 1)
            lines += 1
        self.curpos = self.file.tell()

    def _get_curpos(self):
        '''assigns curpos'''
        if self.bytes_num:
            self.curpos = self.bytes_num
        else:
            self.curpos = self._get_line_pos()

    def _reader(self, f):
        f.seek(self.curpos)
        line = f.readline()
        if not line:
            f.seek(self.curpos)
            time.sleep(self.sleep_val)
        else:
            self.callback(line)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-c',
                   '--bytes',
                   dest    = 'bytes_num',
                   type    = int,
                   default = None,
                   help    = "output starting with a byte NUM of each file")
    p.add_argument('-f',
                   '--follow',
                   dest    = 'follow',
                   default = False,
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
    p.add_argument('filenames', nargs='*')
    args = p.parse_args()
    assert (args.bytes_num is None) & (args.lines_num == LINES), (
        'Cant take lines and bytes offset at the same time')
    filenames = []
    for file in args.filenames:
        d = Tailor(file, args.bytes_num, args.follow, args.lines_num,
                   args.sleep_val)
