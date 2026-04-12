"""Compatibility module that forwards to `ruz_server.main`."""

import runpy

if __name__ == "__main__":
    runpy.run_module("ruz_server.main", run_name="__main__")
