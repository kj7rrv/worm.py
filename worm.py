#!/usr/bin/env python3

import sys
import random
import time
import contextlib
import termios
import timeout_decorator
import os
import argparse
import json
import info
from blessings import Terminal


class QuitGameError(BaseException):
    pass


class RanIntoSomethingError(QuitGameError):
    pass


def draw_worm():
    for location in worm_locations:
        print(do_move(*reversed(location)) + term.bright_blue('o'), end='')

    print(do_move(*reversed(worm_head)) + '@' + do_move(*reversed(worm_head)), end='')


def draw_frame():
    print(term.clear, end='')
    print(do_move(0, 0) + term.on_red(' worm') + term.bright_cyan_on_red('.py ') + ' Press ' + term.bold_green('I') + ' for info, ' + term.bold_red('Ctrl-C')+ ' to quit', end='')
    if score > -1:
        print(do_move(0, width-12) + f'Score:{" "*(4-len(str(score)))}{term.bright_green(str(score))}', end='')
    print(do_move(1, 0) + term.white_on_red('┌' + ('─' * (width-3)) + '┐'), end='')
    for y in range(2, height-1):
        print(do_move(y, 0) + term.white_on_red('│' + do_move(y, width-2) + '│'), end='')
    print(
            do_move(height-1, 0)
            + term.white_on_red('└')
            + term.white_on_red('─' * (width-3))
            + term.white_on_red('┘')
        , end='')
    print(do_move(*reversed(bonus_location)) + term.black_on_green(term.on_bright_green(str(bonus_points))), end='')
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
    
    save_game()

    k = await_keys('hjklHJKLABCDwasdiI')
    if k in 'hjklHJKLABCDwasd':
        move_head(k, 10 if k in 'HJKL' else 1)
        draw_frame()
        do_automove = False
        return
    elif k in '':
        save_game()
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


def do_move(y, x):
    y += (term.height - height) // 2
    x += (term.width - width) // 2
    return term.move(y, x)


def save_game():
    if args.save:
        with open(gamesave_path, 'w+') as f:
            json.dump([worm_locations, worm_head, last_dir, score, size, bonus_location, bonus_points, do_automove, do_help], f)


term = Terminal()
gamesave_path = os.path.join(os.getenv('HOME'), '.worm.py-gamesave')

parser = argparse.ArgumentParser()
parser.add_argument("--length", '-l', help="initial worm length (default 7)", default=7, type=int)
parser.add_argument("--save", '-s', help="enable game saving (sets screen size to 80x24)", action='store_true')
parser.add_argument("--delete-save", help="delete saved game and exit", action='store_true')
args = parser.parse_args()

if args.delete_save:
    try:
        os.unlink(gamesave_path)
        print("Saved game deleted.")
    except FileNotFoundError:
        print("No saved game found.")
    except Exception as e:
        print("An error occurred.")
        print(str(type(e)).split("'")[1] + ': ' + str(e))
        sys.exit(1)
    sys.exit(0)

if args.save:
    height = 24
    width = 80
else:
    height = term.height
    width = term.width

worm_y = height // 2
x_offset = (term.width - width) // 2
info_1, info_2 = info.get_infos(term, do_move, height, width, x_offset)
try:
    if not args.save:
        raise FileNotFoundError() #TODO: this is not pythonic

    with open(gamesave_path) as f:
        save = json.load(f)
        worm_locations, worm_head, last_dir, score, size, bonus_location, bonus_points, do_automove, do_help = save
except FileNotFoundError:
    size = args.length
    worm_locations = [[i+10, worm_y] for i in range(size)]
    worm_head = [size+10, worm_y]
    last_dir = 'x'
    score = 0
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
                        save_game()
                        sys.exit(0)

                do_help = False
            else:
                try:
                    run()
                except timeout_decorator.timeout_decorator.TimeoutError:
                    pass
except KeyboardInterrupt:
    save_game()
    sys.exit(0)
except RanIntoSomethingError:
    try:
        if args.save:
            os.unlink(gamesave_path)
    except FileNotFoundError:
        pass
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
