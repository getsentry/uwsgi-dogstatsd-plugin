from __future__ import annotations

import os.path
import subprocess
import sys
import time
import urllib.request

import ephemeral_port_reserve

# https://github.com/lincolnloop/pyuwsgi-wheels/pull/17
UWSGI_PROG = """\
import os
import sys

orig = sys.getdlopenflags()
sys.setdlopenflags(orig | os.RTLD_GLOBAL)
import pyuwsgi
sys.setdlopenflags(orig)

pyuwsgi.run()
"""

PLUGIN_LOC = os.path.join(sys.prefix, "lib", "dogstatsd_plugin.so")

APP_PY = """\
def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [b"Hello World"]
"""


def test_it_can_start(tmp_path):
    tmp_path.joinpath("app.py").write_text(APP_PY)

    port = ephemeral_port_reserve.reserve()
    proc = subprocess.Popen(
        (
            sys.executable,
            "-c",
            UWSGI_PROG,
            f"--http=127.0.0.1:{port}",
            "--enable-metrics",
            "--stats-push=dogstatsd:127.0.0.1:8125,myapp",
            "--wsgi-file=app.py",
        ),
        env={**os.environ, "UWSGI_NEED_PLUGIN": PLUGIN_LOC},
        cwd=tmp_path,
    )
    try:
        for _ in range(100):
            if proc.poll():
                raise AssertionError(f"unexpected early exit: {proc.poll()}")
            try:
                resp = urllib.request.urlopen(f"http://127.0.0.1:{port}")
            except OSError:
                print("...waiting for startup")
                time.sleep(0.1)
            else:
                assert resp.read() == b"Hello World"
                break
        else:
            raise AssertionError("timeout starting app")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
