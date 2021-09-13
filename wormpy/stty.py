import subprocess

def stty(raw=None, echo=None):
    args = ['stty']

    if raw is not None:
        args.append('raw' if raw else '-raw')

    if echo is not None:
        args.append('echo' if echo else '-echo')

    subprocess.run(args)
