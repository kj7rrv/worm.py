#!/usr/bin/env python3

import sys
import random
import time
import contextlib
import termios
import timeout_decorator
import os
from blessings import Terminal


class QuitGameError(BaseException):
    pass


class RanIntoSomethingError(QuitGameError):
    pass


def draw_worm():
    for location in worm_locations:
        print(term.move(*reversed(location)) + term.bright_blue('o'), end='')

    print(term.move(*reversed(worm_head)) + '@' + term.move(*reversed(worm_head)), end='')


def draw_frame():
    print(term.clear, end='')
    print(term.move(0, 0) + term.on_red(' worm') + term.bright_cyan_on_red('.py ') + ' Press ' + term.bold_green('I') + ' for info, ' + term.bold_red('Ctrl-C')+ ' to quit', end='')
    if score > -1:
        print(term.move(0, width-12) + f'Score:{" "*(4-len(str(score)))}{term.bright_green(str(score))}', end='')
    print(term.move(1, 0) + term.white_on_red('┌' + ('─' * (width-3)) + '┐'), end='')
    for y in range(2, height-1):
        print(term.move(y, 0) + term.white_on_red('│' + term.move(y, width-2) + '│'), end='')
    print(
            term.move(height-1, 0)
            + term.white_on_red('└')
            + term.white_on_red('─' * (width-3))
            + term.white_on_red('┘')
        , end='')
    print(term.move(*reversed(bonus_location)) + term.black_on_green(term.on_bright_green(str(bonus_points))), end='')
    draw_worm()
    sys.stdout.flush()


def move_head(direction, distance):
    global size, worm_head, last_dir, worm_locations, bonus_location, bonus_points, score

    if direction not in 'hjklHJKLABCDwasdx':
        raise ValueError('argument to move_head() must be one of `hjklHJKLABCDwasdx`')

    if direction == 'x':
        return

    worm_locations.append(worm_head.copy())
    
    worm_head = worm_head.copy()

    if direction in 'kKAw': #up
        worm_head[1] -= 1
        last_dir = 'A'
    elif direction in 'jJBs': #down
        worm_head[1] += 1
        last_dir = 'B'
    elif direction in 'hHDa': #left
        worm_head[0] -= 1
        last_dir = 'D'
    elif direction in 'lLCd': #right
        worm_head[0] += 1
        last_dir = 'C'
    
    while len(worm_locations) > size:
        worm_locations.pop(0)

    if worm_head in worm_locations \
            or worm_head[1] <= 1 \
            or worm_head[1] >= height-1 \
            or worm_head[0] <= 0 \
            or worm_head[0] >= width-2:
        raise RanIntoSomethingError()

    if worm_head == bonus_location:
        size += bonus_points
        score += bonus_points
        new_bonus()

    if distance > 1:
        move_head(direction, distance-1)


@contextlib.contextmanager
def decanonize(fd):
    old_settings = termios.tcgetattr(fd)
    new_settings = old_settings[:]
    new_settings[3] &= ~termios.ICANON
    termios.tcsetattr(fd, termios.TCSAFLUSH, new_settings)
    yield
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_settings)


@timeout_decorator.timeout(1)
def run(*_):
    global do_automove, do_help
    if do_automove:
        move_head(last_dir, 1)
        draw_frame()

    do_automove = True

    k = await_keys('hjklHJKLABCDwasdiI')
    if k in 'hjklHJKLABCDwasd':
        move_head(k, 10 if k in 'HJKL' else 1)
        draw_frame()
        do_automove = False
        return
    elif k in '':
        sys.exit(0)
    elif k in 'iI':
        do_help = True
        return


def await_keys(keys):
    while True:
        k = sys.stdin.read(1)
        if k in keys:
            return k


def new_bonus():
    global bonus_location, bonus_points
    bonus_points = random.randint(1, 9)
    bonus_location = worm_head
    while worm_head == bonus_location or bonus_location in worm_locations:
        bonus_location = [
                random.randint(1, width-3),
                random.randint(2, height-2),
                ]


term = Terminal()

height = term.height
width = term.width

info_1 = term.clear() + term.move(0, 0) + term.on_red(' worm') \
        + term.bright_cyan_on_red('.py ') + f''' v1.0: bsdgames worm, ported \
to Python and improved

See https://github.com/kj7rrv/worm.py for source code and installation
instructions.

Thanks to the authors of the following libraries:
    * blessings\t\t{term.blue("https://pypi.org/project/blessings/")}
    * timeout-decorator\t\
{term.blue("https://pypi.org/project/timeout-decorator/")}

Also, thanks to the devolopers of Python and bsdgames worm. It would have been
much harder to port worm to Python if either if either worm or Python did not
exist.

Use the arrow keys or WASD to move. Try to get the green numbers, but don't
let the worm run into itself or the red edge.

To change the initial length of the worm, add the desired length of the worm
after `{term.bright_red('worm')}{term.bright_cyan('.py')}`, as in \
`{term.bright_red('worm')}{term.bright_cyan('.py')} 20` for a twenty-character\
-long worm.

{term.bright_red('worm')}{term.bright_cyan('.py')} is released under the MIT \
license.'''\
+ '{}Press {} to continue, {} to exit the game...'.format(
        term.move(height - 1, 0),
        term.bold_green('C'),
        term.bold_red('Ctrl-C')
        )

info_2 = term.clear() + term.move(0, 0) + term.on_red(' worm') \
        + term.bright_cyan_on_red('.py ') + f''' Copyright and License Info

Copyright (c) 2021 Samuel L. Sloniker

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

''' + term.bold('''THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY \
KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.''') \
+ '{}Press {} to return to the game, {} to exit...'.format(
        term.move(height - 1, 0),
        term.bold_green('C'),
        term.bold_red('Ctrl-C')
        )

last_dir = 'x'

if len(sys.argv) == 2:
    try:
        size = int(sys.argv[1])
        if size <= 0 or size >= width-13:
            size = 7
    except ValueError:
        size = 7
else:
    size = 7

score = 0

worm_y = height // 2

worm_locations = [[i+10, worm_y] for i in range(size)]
worm_head = [size+10, worm_y]

new_bonus()

do_automove = True
do_help = False

try:
    with term.fullscreen():
        os.system('stty raw -echo')
        draw_frame()
        while True:
            if do_help:
                for info in (info_1, info_2):
                    os.system('stty -raw')
                    print(info, end='')
                    sys.stdout.flush()
                    os.system('stty raw')

                    k = await_keys('cC')
                    if k in '':
                        sys.exit(0)

                do_help = False
            else:
                try:
                    run()
                except timeout_decorator.timeout_decorator.TimeoutError:
                    pass
except KeyboardInterrupt:
    sys.exit(0)
except RanIntoSomethingError:
    os.system('stty -raw echo')
    print('', end='\r\n')
    if size + 1 >= (height-3) * (width-1):
        print('You won!', end='\r\n')
    else:
        print('Well, you ran into something and the game is over.', end='\r\n')
    print(f'Your final score was {score}', end='\r\n')
    print('', end='\r\n')
finally:
    os.system('stty -raw echo')
