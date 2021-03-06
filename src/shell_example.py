#!/usr/bin/python3
import sys
from shell import Function, set_functions, shell, main
from util import has_output
import cli

use_shell_with_history = True


def f(x: int): return x
def g(x: int, y=1): return x + y
def h(x: int, y: float, z): return x + y * z


def example(a: int, b, c: float = 3.):
    """An example of a function with a docstring

    Parameters
    ----------
        a: positive number
        b: object
    """
    return a


functions = {
    'a_long_function': f,
    'another_function': f,
    'f': f,
    'g': g,
    'h': h,
    'example': example,
    'ls': Function(shell('ls'), args={'-latr': 'flags', '[file]': ''}),
    'cat': Function(shell('cat'), args={'file': ''}),
    'vi': Function(shell('vi'), args={'[file]': ''})}


if __name__ == '__main__':
    if has_output(sys.stdin):
        main(functions)
    else:
        # use_shell_with_history:
        set_functions(functions)
        cli.main()
