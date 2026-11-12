import os, ssl, urllib.request
CA = os.path.expanduser("~/.ccr/ca-bundle.crt")
def ssl_ctx():
    return ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()
def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) meridiano-curioso/1.0"})
    return urllib.request.urlopen(req, context=ssl_ctx(), timeout=timeout).read()
