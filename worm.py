import sys
import random
import time
import contextlib
import termios
import timeout_decorator
import os
from blessings import Terminal

term = Terminal()

height = term.height
width = term.width
last_dir = 'x'

class QuitGameError(BaseException):
    pass


class RanIntoSomethingError(QuitGameError):
    pass

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

def draw_worm():
    for location in worm_locations:
        print(term.move(*reversed(location)) + 'o', end='')

    print(term.move(*reversed(worm_head)) + '@' + term.move(*reversed(worm_head)), end='')


def draw_frame():
    print(term.clear, end='')
    print(term.move(0, 1) + 'Worm', end='')
    if score > -1:
        print(term.move(0, width-12) + f'Score:{" "*(4-len(str(score)))}{score}', end='')
    print(term.move(1, 0) + '┌' + ('*' * (width-3)) + '┐', end='')
    for y in range(2, height-1):
        print(term.move(y, 0) + '*' + term.move(y, width-2) + '*', end='')
    print(term.move(height-1, 0) + '└' + ('*' * (width-3)) + '┘', end='')
    print(term.move(*reversed(bonus_location)) + str(bonus_points), end='')
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
        bonus_points = random.randint(1, 9)
        while worm_head == bonus_location or bonus_location in worm_locations:
            bonus_location = [
                    random.randint(1, width-3),
                    random.randint(2, height-2),
                    ]

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

worm_y = height // 2

worm_locations = [[i+10, worm_y] for i in range(size)]
worm_head = [size+10, worm_y]

bonus_points = random.randint(1, 9)
bonus_location = worm_head
while worm_head == bonus_location or bonus_location in worm_locations:
    bonus_location = [
            random.randint(1, width-3),
            random.randint(2, height-2),
            ]


do_automove = True

@timeout_decorator.timeout(1)
def run(*_):
    global do_automove
    if do_automove:
        move_head(last_dir, 1)
        draw_frame()

    do_automove = True

    while True:
        k = sys.stdin.read(1)
        if k in 'hjklHJKLABCDwasd':
            move_head(k, 10 if k in 'HJKL' else 1)
            draw_frame()
            do_automove = False
            return
        elif k in '':
            # That string is Ctrl-C Ctrl-\, in case you editor doesn't handle
            # control characters as well as Vim does.
            sys.exit(0)

try:
    with term.fullscreen():
        os.system('stty raw -echo')
        draw_frame()
        while True:
            try:
                run()
            except timeout_decorator.timeout_decorator.TimeoutError:
                pass
except KeyboardInterrupt:
    sys.exit(0)
except RanIntoSomethingError:
    os.system('stty -raw echo')
    print('', end='\r\n')
    print('Well, you ran into something and the game is over.', end='\r\n')
    print(f'Your final score was {score}', end='\r\n')
    print('', end='\r\n')
finally:
    os.system('stty -raw echo')
