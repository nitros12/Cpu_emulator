import curses
import glob
import os
from curses import newpad, newwin, wrapper

from components import *

MEM_SIZE = 150

files = glob.glob(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "example_programs", "*.txt"))

filedict = {}

for i, c in enumerate(files):
    print("{}: {}".format(i, c.split(os.pathsep)[-1]))
    filedict[str(i)] = c  # generate dict here for ease of entering input

while True:
    program = filedict.get(input("Index of program to run: "))
    if program:
        break


with open(program) as commandList:
    commands = [i.strip("\n") for i in list(commandList)]

myprogram = Compiler(commands, MEM_SIZE)

mycpu = Cpu(MEM_SIZE, myprogram.compiled)


def displayStack(scrn, stk):
    scrn.clear()

    if not stk:
        return

    max_width = max(map(lambda a: len(str(a)), stk))

    for b, (c, i ) in enumerate(list(enumerate(stk))[-40:]):
        scrn.addstr(b, 0, f"{MEM_SIZE-c-1:^5} -> |{i:^{max_width}}|")

    scrn.refresh()


def displayRegs(scrn, regs):
    scrn.clear()
    max_width = max(map(lambda a: len(str(a)), regs.values()))
    for i, (j, k) in enumerate(regs.items()):
        scrn.addstr(i, 0, f"{j:^5} -> |{k:^{max_width}}|")

    scrn.refresh()

def displayCmd(scrn):
    scrn.clear()

    scrn.addstr(0, 0, mycpu.last_opcode)
    scrn.refresh()


def showStdout(scrn):
    scrn.clear()

    for c, i in enumerate(mycpu.stdout[-20:]):
        scrn.addstr(c, 0, i)
    scrn.refresh()

def main(stdscr):
    # Clear screen
    stdscr.clear()

    stack = stdscr.derwin(44, 20, 0, 60)
    regs = stdscr.derwin(20, 20, 0, 0)
    stuff = stdscr.derwin(20, 25, 21, 0)
    stdout = stdscr.derwin(20, 20, 20, 26)

    while True:
        displayStack(
                stack, mycpu.memory.cells[MEM_SIZE:mycpu.registers["stk"]-1:-1])
        displayRegs(regs, mycpu.registers.registers)
        displayCmd(stuff)
        showStdout(stdout)
        stdscr.refresh()
        stdscr.getkey()
        mycpu.run_once()

wrapper(main)
