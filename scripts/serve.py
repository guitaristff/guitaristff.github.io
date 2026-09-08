"""Serve the public build on localhost. Run: python scripts/serve.py"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from build import build


def main():
    parser = argparse.ArgumentParser(description="Preview Zhaofeng Du's personal website")
    parser.add_argument("--port", type=int, default=4173)
    args = parser.parse_args()
    output = build()
    handler = partial(SimpleHTTPRequestHandler, directory=str(output))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Preview: http://localhost:{args.port}", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Preview stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
