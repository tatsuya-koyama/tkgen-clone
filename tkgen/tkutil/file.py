# -*- coding: utf-8 -*-
"""
tkutil/file
    [ToDo]

@copyright: 2011 by Tatsuya Koyama
            (www.tatsuya-koyama.com)
"""

import os, fnmatch, time
import cPickle
from console import cprint

def get_all_files(root_dir, patterns='*', single_level=False, yield_folders=False):
    """
    traverse file tree and get paths that mathced patterns.
    """
    # convert to list from ';' separated string
    patterns = patterns.split(';')
    for path, sub_dirs, files in os.walk(root_dir):
        if yield_folders:
            files.extend(sub_dirs)
        files.sort()
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    yield os.path.join(path, name)
                    break
        if single_level:
            break

def get_timestamp(file_path):
    #stat = os.stat(file_path)
    #timestamp = time.strftime("%Y/%m/%d", time.localtime(stat[ST_MTIME]))
    timestamp = os.stat(file_path).st_mtime
    formatted_timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime(timestamp))
    return formatted_timestamp

def save_obj_to_file(obj, file_path):
    fh = file(file_path, 'wb')
    cPickle.dump(obj, fh)
    fh.close()

def load_obj_from_file(file_path):
    obj = None
    try:
        fh = file(file_path, 'rb')
        obj = cPickle.load(fh)
    except IOError:
        cprint("<red:load file not found: %s/>" % file_path)
        pass
    return obj
