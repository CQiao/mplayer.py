#!/usr/bin/env python
# $Id$

"""MPlayer remote control client"""

__version__ = "$Revision$"

__copyright__ = """
Copyright (C) 2007-2008  The MA3X Project (http://bbs.eee.upd.edu.ph)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


try:
    import socket
    import sys
    import re
    from optparse import OptionParser
except ImportError, msg:
    exit(msg)
from pymplayer import Client, PORT, MAX_CMD_LENGTH
try:
    import curses
except ImportError:
    curses = None
else:
    command_map = {
        ord('q'): "quit", ord('Q'): "quit", 27: "quit",
        ord('p'): "pause", ord('P'): "pause", ord(' '): "pause",
        ord('m'): "mute", ord('M'): "mute",
        ord('f'): "vo_fullscreen", ord('F'): "vo_fullscreen",
        ord('o'): "osd", ord('O'): "osd",
        ord('r'): "reload", ord('R'): "reload",
        curses.KEY_LEFT: "seek -5",
        curses.KEY_RIGHT: "seek +5",
        curses.KEY_NPAGE: "pt_step -1",
        curses.KEY_PPAGE: "pt_step +1",
        curses.KEY_UP: "volume +2",
        curses.KEY_DOWN: "volume -2",
        curses.KEY_HOME: "seek 0 1",
        curses.KEY_END: "seek 100 1"}


def start_ui(peername):
    stdscr = curses.initscr()

    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)

    stdscr.addstr("".join(['client.py ', __version__, '\n']))
    stdscr.addstr("Connected to %s at port %d\n" % peername)

    stdscr.addstr("\n     Controls:\n")
    stdscr.addstr("\t     Esc, q - quit\n")
    stdscr.addstr("\tspacebar, p - pause\n")
    stdscr.addstr("\t          m - mute\n")
    stdscr.addstr("\t          o - osd\n")
    stdscr.addstr("\t          f - fullscreen\n")
    stdscr.addstr("\t          r - restart MPlayer\n")
    stdscr.addstr("\t          : - input command\n")

    stdscr.addstr(3, 38, "\t        up - volume up\n")
    stdscr.addstr(4, 38, "\t      down - volume down\n")
    stdscr.addstr(5, 38, "\t      left - seek -5s\n")
    stdscr.addstr(6, 38, "\t     right - seek +5s\n")
    stdscr.addstr(7, 38, "\t      home - go to beginning of track\n")
    stdscr.addstr(8, 38, "\t       end - go to end of track\n")
    stdscr.addstr(9, 38, "\t   page up - next track\n")
    stdscr.addstr(10, 38, "\t page down - previous track\n")

    return stdscr


def end_ui(stdscr):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def main():
    cl_usage = "%prog [OPTIONS] [COMMAND]"
    cl_ver = "".join(['%prog ', __version__])

    parser = OptionParser(usage=cl_usage, version=cl_ver)

    parser.add_option("-c", "--command", dest="command", help="send CMD to the MPlayer server", metavar='"CMD"')
    parser.add_option("-n", "--no-curses", dest="curses", default=True, action="store_false", help="don't use curses interface")
    parser.add_option("-H", "--host", dest="host", default="localhost", help="server to connect to")
    parser.add_option("-p", "--port", dest="port", default=PORT, type="int", help="server port to connect to")

    (options, args) = parser.parse_args()

    if curses is None:
        options.curses = False
    if not options.curses and options.command is None:
        parser.error("not using curses but no command specified")

    client = Client(options.host, options.port)
    client.connect()
    try:
        peername = client.getpeername()
    except socket.error, msg:
        sys.exit(msg)

    if options.curses and options.command is None:
        stdscr = start_ui(peername)
        # Just a string of spaces
        spaces = "         ".join(["         " for x in range(10)])

    while True:
        if options.curses and options.command is None:
            stdscr.addstr(12, 0, "Command: ")
            try:
                c = stdscr.getch()
            except KeyboardInterrupt:
                c = ord('q')
            if c == ord(':'):
                curses.echo()
                stdscr.addstr(12, 0, "".join(['Command: ', spaces]))
                try:
                    cmd = stdscr.getstr(12, 9, MAX_CMD_LENGTH)
                except KeyboardInterrupt:
                    cmd = ""
                curses.noecho()
            else:
                try:
                    cmd = command_map[c]
                except KeyError:
                    continue
            if c != ord(':'):
                stdscr.addstr(12, 9, "".join([cmd, spaces]))
                stdscr.move(12, 9)
        else:
            cmd = options.command
        # Zero-length command
        if not cmd:
            if options.curses and options.command is None:
                continue
            else:
                break

        try:
            if not client.send_command(cmd):
                break
        except socket.error, msg:
            break
        if options.command is not None:
            break

    if options.curses and options.command is None:
        end_ui(stdscr)

    client.close()

    try:
        print >> sys.stderr, msg
    except NameError:
        pass


if __name__ == "__main__":
    main()
