#!/usr/bin/python3
import sys
from typing import Tuple
from quo.completion import NestedCompleter
from quo.history import MemoryHistory
from quo.prompt import Prompt
from quo.text import Text

from shell import Shell, run_command, ShellException
from util import infer_synopsis

rprompt_init = 'Type any command to continue'
rprompt_default = ''
rprompt_error = 'Type `help` or ? for help'


def main():
    session, shell = setup()
    run(session, shell)


def setup() -> Tuple[Prompt, Shell]:
    shell = Shell()
    shell.ignore_invalid_syntax = False

    # setup a completion-dropdown
    completer = NestedCompleter.add({k: None for k in Shell.all_commands()})

    # setup a history-completion
    for cmd in Shell.all_commands():
        MemoryHistory.append(cmd)

    session = Prompt(
        history=MemoryHistory,
        suggest="history",
        rprompt=Text(rprompt_init),
        enable_history_search=True,
        completer=completer,
        vi_mode=True,
        bottom_toolbar=lambda: toolbar(shell)
    )
    return session, shell


def run(session: Prompt, shell: Shell):
    print('Press ctrl-d to exit, ctrl-c to cancel and TAB for word completion')
    while True:
        step(session, shell)


def step(session, shell):
    try:
        cmd = session.prompt('$ ')
        try:
            run_command(cmd, shell)
            session.rprompt = Text(rprompt_default)
        except ShellException as e:
            print(e)
            session.rprompt = Text(rprompt_error)
    except KeyboardInterrupt:
        pass
    except EOFError:
        sys.exit(1)


def toolbar(shell: Shell, text='Run any command to show info'):
    method = shell.last_method()
    if method:
        text = generate_help(method)

    return Text(text)


def generate_help(func):
    synopsis = infer_synopsis(func)
    full_text = synopsis
    if func.__doc__:
        full_text += f'  |  {func.__doc__}'

    # keep the first few lines
    return '\n'.join(full_text.split('\n')[:3])


if __name__ == '__main__':
    main()
