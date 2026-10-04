"""Serve this exact release on a free localhost port; no collisions with older previews."""
import argparse,http.server,webbrowser
from functools import partial
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--no-browser',action='store_true');a=p.parse_args()
    handler=partial(http.server.SimpleHTTPRequestHandler,directory=str(Path(__file__).resolve().parent/'ui'))
    with http.server.ThreadingHTTPServer(('127.0.0.1',0),handler) as server:
        url='http://127.0.0.1:'+str(server.server_port)+'/'
        print('Housing Navigator publication preview: '+url,flush=True)
        print('Keep this window open. Press Ctrl+C to stop the preview.',flush=True)
        if not a.no_browser:webbrowser.open(url)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
if __name__=='__main__':main()
