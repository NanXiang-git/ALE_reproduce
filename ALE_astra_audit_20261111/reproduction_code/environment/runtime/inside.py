"""Sandbox-local bridge; stdout/stdin are a credential-free host RPC pipe."""
import base64, ctypes, http.server, json, os, pathlib, socket, subprocess, sys, threading, time

ctypes.CDLL(None).prctl(4, 0, 0, 0, 0)  # No ptrace/read of supervisor descriptors.
LOCK = threading.RLock()

def send(obj):
    sys.stdout.write(json.dumps(obj, separators=(',', ':')) + '\n')
    sys.stdout.flush()

def event(obj):
    with LOCK:
        send({'op': 'event', **obj})

class Bridge(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    def log_message(self, *args):
        pass
    def do_GET(self):
        self.send_error(403, 'Only controlled POST endpoints are available')
    def do_POST(self):
        if self.path not in ('/v1/responses',):
            self.send_error(403, 'Endpoint is not allowed')
            return
        length = int(self.headers.get('Content-Length', '0'))
        if not 0 < length <= 90_000_000:
            self.send_error(413)
            return
        body = json.loads(self.rfile.read(length))
        with LOCK:
            send({'op': 'http', 'path': self.path, 'body': body})
            first = json.loads(sys.stdin.readline())
            self.send_response(first['status'])
            self.send_header('Content-Type', first.get('content_type', 'application/json'))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.close_connection = True
            while True:
                part = json.loads(sys.stdin.readline())
                if part.get('done'):
                    break
                try:
                    self.wfile.write(base64.b64decode(part['chunk']))
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    # Drain protocol even if Codex disconnects.
                    pass

def checks():
    result = {'input_readable': pathlib.Path('/candidate/TASK.md').is_file()}
    try:
        pathlib.Path('/candidate/.write_probe').write_text('x')
        result['input_readonly'] = False
    except OSError:
        result['input_readonly'] = True
    p = pathlib.Path('/workspace/submission/write_probe')
    p.write_text('ok'); result['submission_writable'] = p.read_text() == 'ok'; p.unlink()
    result['host_paths_hidden'] = all(not pathlib.Path(x).exists() for x in (
        '/mnt/c', '/mnt/d', '/home/asus', '/evaluator', '/authoring', '/host_canary', '/root/.codex'))
    result['credential_absent'] = all('API_KEY' not in x for x in os.environ)
    result['network_blocked'] = False
    result['no_network_interfaces'] = set(x.name for x in pathlib.Path('/sys/class/net').iterdir()) <= {'lo'} if pathlib.Path('/sys/class/net').exists() else True
    result['no_default_route'] = len(pathlib.Path('/proc/net/route').read_text().splitlines()) <= 1
    s = socket.socket(); s.settimeout(1)
    try:
        s.connect(('1.1.1.1', 443))
    except OSError:
        result['network_blocked'] = True
    finally:
        s.close()
    result['visible_process_count'] = len([x for x in pathlib.Path('/proc').iterdir() if x.name.isdigit()])
    result['pid_namespace_small'] = result['visible_process_count'] < 12
    event({'event': 'isolation_checks', 'checks': result})
    if not all(v for k, v in result.items() if k != 'visible_process_count'):
        raise RuntimeError('Isolation check failed')

server = http.server.ThreadingHTTPServer(('127.0.0.1', 8765), Bridge)
threading.Thread(target=server.serve_forever, daemon=True).start()
checks()
mode = sys.argv[1]
if mode == 'tools':
    import cv2, numpy, scipy, PIL, docx
    event({'event':'dependencies_verified','cv2':cv2.__version__,'numpy':numpy.__version__,'docx':docx.__version__})
    import urllib.request,urllib.error
    for body in [
        {'model':'wrong-model','reasoning':{'effort':'high'},'input':'x'},
        {'model':'gpt-6-astra','reasoning':{'effort':'high'},'tools':[{'type':'web_search'}],'input':'x'},
        {'model':'gpt-6-astra','reasoning':{'effort':'high'},'input':[{'type':'input_image','image_url':'https://example.com/image.png'}]},
        {'model':'gpt-6-astra','reasoning':{'effort':'high'},'previous_response_id':'unrelated','input':'x'}]:
        req=urllib.request.Request('http://127.0.0.1:8765/v1/responses',json.dumps(body).encode(),{'Content-Type':'application/json'})
        try:urllib.request.urlopen(req,timeout=10);raise RuntimeError('Forbidden request was accepted')
        except urllib.error.HTTPError as e:assert e.code==502
    event({'event':'gateway_restrictions_verified','rejected_requests':4})
    os._exit(0)
if mode == 'killcheck':
    child = subprocess.Popen(['/usr/bin/python3', '-c', "import time,pathlib; p=pathlib.Path('/workspace/heartbeat');\nwhile True: p.write_text(str(time.time())); time.sleep(.2)"])
    event({'event': 'killcheck_started', 'child_pid': child.pid})
    time.sleep(3600)
    raise SystemExit(1)

binary = '/runtime/codex_dist/package/vendor/x86_64-unknown-linux-musl/bin/codex'
prompt = pathlib.Path('/runtime/prompt.txt').read_text() if mode == 'official' else (
 'Infrastructure test only. Execute python to print 7*8; use view_image on /candidate/visual.png and read the six-character code. '
 'Verify Python imports cv2,numpy,scipy,PIL,docx. Write the arithmetic result and image code to /workspace/submission/smoke.txt. Do not spawn subagents.')

args = [binary, 'exec', '--ignore-user-config', '--ignore-rules', '--ephemeral', '--skip-git-repo-check',
        '--dangerously-bypass-approvals-and-sandbox', '--json', '--color', 'never', '--cd', '/workspace',
        '--model', 'gpt-6-astra', '-c', 'model_reasoning_effort="high"',
        '-c', 'model_provider="isolated_gateway"',
        '-c', 'model_providers.isolated_gateway.name="Isolated host gateway"',
        '-c', 'model_providers.isolated_gateway.base_url="http://127.0.0.1:8765/v1"',
        '-c', 'model_providers.isolated_gateway.wire_api="responses"',
        '-c', 'model_providers.isolated_gateway.requires_openai_auth=false',
        '-c', 'features.multi_agent=false', '-c', 'web_search="disabled"',
        '--output-last-message', '/workspace/final_message.txt', prompt]
start = time.monotonic()
event({'event': 'codex_start', 'utc': time.time(), 'mode': mode, 'model': 'gpt-6-astra', 'effort': 'high'})
proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        text=True, encoding='utf-8', errors='replace', start_new_session=True)
def drain_err():
    for line in proc.stderr:
        event({'event': 'codex_stderr', 'line': line.rstrip()})
threading.Thread(target=drain_err, daemon=True).start()
for line in proc.stdout:
    event({'event': 'codex_jsonl', 'line': line.rstrip()})
code = proc.wait()
event({'event': 'codex_exit', 'returncode': code, 'elapsed_seconds': time.monotonic() - start})
os._exit(code)
