def get_infos(term, do_move, height, width, x_offset):
    info_1 = term.clear() + do_move(0, 0) + term.on_red(' Worm') \
            + term.black_on_bright_cyan('.py ') + f''' v1.0: bsdgames worm, ported \
to Python and improved

See https://github.com/kj7rrv/wormpy for source code and installation
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
after `{term.bright_red('worm')}{term.bright_cyan('py')}`, as in \
`{term.bright_red('worm')}{term.bright_cyan('py')} 20` for a twenty-character\
-long worm.

{term.bright_red('Worm')}{term.bright_cyan('.py')} is released under the MIT \
license.'''\
    + '{}Press {} to continue, {} to exit the game...'.format(
            do_move(height - 1, 0),
            term.bold_green('C'),
            term.bold_red('Ctrl-C')
            )

    info_2 = term.clear() + do_move(0, 0) + term.on_red(' Worm') \
            + term.black_on_bright_cyan('.py ') + f''' Copyright and License Info

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
            do_move(height - 1, 0),
            term.bold_green('C'),
            term.bold_red('Ctrl-C')
            )
    info_1 = info_1.replace('\n', '\n' + term.move_x(x_offset))
    info_2 = info_2.replace('\n', '\n' + term.move_x(x_offset))
    return info_1, info_2
