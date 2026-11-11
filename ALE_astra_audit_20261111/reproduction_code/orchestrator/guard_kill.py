import json,os,pathlib,signal,sys
root=pathlib.Path(__file__).resolve().parents[1]
pid=int(sys.argv[1]);case=sys.argv[2]
try:
    args=(pathlib.Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
    if args[0] != b'bwrap' or str(root/'solver'/case).encode() not in args:
        raise RuntimeError('PID does not match the expected isolated case')
    os.killpg(pid,signal.SIGKILL)
    print(json.dumps({'killed':pid,'case':case}))
except FileNotFoundError:
    print(json.dumps({'already_exited':pid,'case':case}))
