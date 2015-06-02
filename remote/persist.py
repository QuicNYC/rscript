__author__ = 'eric'
import cPickle
import os.path
from collections import defaultdict
from local_settings import CONNEXION_PATH
PREFIX = CONNEXION_PATH + "/databases/"

def get_catalog():
    if os.path.isfile(PREFIX + 'catalog.cf'):
        f = open(PREFIX + 'catalog.cf')
        catalog = cPickle.load(f)
        f.close()
    else:
        catalog = defaultdict()
    return catalog

def set_catalog(cat):
    f = open(PREFIX+'catalog.cf','w')
    cPickle.dump(cat,f)
    f.close()

def load_config(name):
    if get_catalog().has_key(name):
        f = open(PREFIX + name +'.cf')
        ret = cPickle.load(f)
        f.close()
        return ret
    else:
        return defaultdict()

def save_config(name, cont):
    catalog = get_catalog()
    if not catalog.has_key(name):
        catalog[name] = 1
        set_catalog(catalog)
    f = open(PREFIX + name+'.cf',"w")
    cPickle.dump(cont,f)
    f.close()
    return catalog.keys()

def get_config_list():
   return get_catalog().keys()
