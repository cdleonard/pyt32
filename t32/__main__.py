#! /usr/bin/env python3

import sys

from argparse import ArgumentParser
from . import get_t32

def create_parser():
    parser = ArgumentParser()

    sub = parser.add_subparsers(dest='subcmd')

    subparser = sub.add_parser('run', help="Run a command and wait for execution (unlike t32rem)")
    subparser.add_argument('cmd', nargs='+')

    subparser = sub.add_parser('echo', help="Call a function and print the result to stdout")
    subparser.add_argument('arg')

    subparser = sub.add_parser('wait', help="Wait for pending command execution."
            " This specificially waits T32_GetPracticeState() reports NOT_RUNNING")

    subparser = sub.add_parser('winprint', help="Print a window to stdout")
    subparser.add_argument('cmd', nargs='+')

    subparser = sub.add_parser('areacat', help="Print an AREA to stdout")
    subparser.add_argument('area_name', nargs='?', default='A000')

    return parser

def parse_args(argv):
    return create_parser().parse_args(argv)

def invoke(argv, t32):
    opts = parse_args(argv)
    if opts.subcmd == 'run':
        t32.run(opts.cmd)
    elif opts.subcmd == 'echo':
        sys.stdout.write(str(t32.echo(opts.arg)))
    elif opts.subcmd == 'wait':
        t32.wait()
    elif opts.subcmd == 'winprint':
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix='.pyt32.winprint.txt') as tmp:
            t32.run(['PRinTer.FILE', tmp.name, '/Append'])
            t32.run(['WinPrint.' + opts.cmd[0]] + opts.cmd[1:])
            with open(tmp.name) as fd:
                sys.stdout.write(fd.read())
    elif opts.subcmd == 'areacat':
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix='.pyt32.areasave.txt') as tmp:
            t32.dowait(['AREA.SAVE', opts.area_name, tmp.name])
            with open(tmp.name) as fd:
                sys.stdout.write(fd.read())
    else:
        raise Exception("Unknown subcmd {}".format(opts.subcmd))

def main(argv=None):
    with get_t32() as t32:
        invoke(argv, t32)

if __name__ == '__main__':
    main()
