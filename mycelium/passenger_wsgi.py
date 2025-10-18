import importlib.machinery
import importlib.util
import os
import sys
import environ


sys.path.insert(0, os.path.dirname(__file__))

def load_source(modname, filename):
    loader = importlib.machinery.SourceFileLoader(modname, filename)
    spec = importlib.util.spec_from_file_location(modname, filename, loader=loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

# Load environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '.env'))

# Determine run mode
RUN_MODE = env('RUN_MODE', default='local')

# Set up WSGI based on RUN_MODE
if RUN_MODE == 'local':
    wsgi = load_source('wsgi', 'config/wsgi.py')
else:
    wsgi = load_source('config_wsgi', 'config/wsgi.py')

application = wsgi.application
print(f"Loaded wsgi module for RUN_MODE={RUN_MODE}:", wsgi)