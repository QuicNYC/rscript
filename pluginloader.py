__author__ = 'eric'
import io
import settings
from local_settings import PLUGIN_PATH

def importCode(code,name,add_to_sys_modules=0):
    import sys,imp
    module = imp.new_module(name)

    exec code in module.__dict__
    if add_to_sys_modules:
        sys.modules[name] = module
    return module


def savePlug(text):
    f = open(PLUGIN_PATH+'plugins.py','w')
    f.write(text)
    print 'file', PLUGIN_PATH+'plugins.py saved'
    return f

def reload():
    f = open(PLUGIN_PATH+"plugins.py")
    mod = importCode(f,"plugins",1)
    return mod


def upload(text):
    savePlug(text)
    return reload()


