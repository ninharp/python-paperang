#!/usr/bin/python3
# -*-coding:utf-8-*-
import os
import pathlib

class Hooks:
    hooks = []

    def __init__(self, address=None):
        hook_dir = f'{pathlib.Path(__file__).parent.resolve()}/hooks'
        for path in os.listdir(hook_dir):
            file_path = os.path.join(hook_dir, path)
            if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                self.hooks.append(file_path)

    def run_hooks(self):
        [os.system(f'{hook}') for hook in self.hooks]
