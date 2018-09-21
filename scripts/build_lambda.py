
from distutils.dir_util import copy_tree

import base64
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

def build(src_dir):
    with tempfile.TemporaryDirectory() as build_dir:
        copy_tree(src_dir, build_dir)
        if os.path.exists(os.path.join(src_dir, 'requirements.txt')):
            subprocess.run(
                [sys.executable,
                 '-m',
                 'pip',
                 'install',
                 '--ignore-installed',
                 '--target', build_dir,
                 '-r', os.path.join(build_dir, 'requirements.txt')],
                 check=True,
                 stdout=subprocess.DEVNULL,
            )
        artifact=tempfile.NamedTemporaryFile(delete=False)
        make_archive(build_dir, artifact)
        return artifact.name


def make_archive(src_dir, archive_file):
    with zipfile.ZipFile(archive_file, 'w') as archive:
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.pyc'):
                    break
                metadata = zipfile.ZipInfo(
                    os.path.join(root, file).replace(src_dir, '')
                )
                with open(os.path.join(root, file), 'rb') as f:
                    data = f.read()
                archive.writestr(
                    metadata,
                    data
                )

def get_hash(archive_file):
    '''
    Return base64 encoded sha256 hash of archive file
    '''
    with open(archive_file, 'rb') as f:
        h = hashlib.sha256()
        h.update(f.read())
    return base64.standard_b64encode(h.digest()).decode('utf-8', 'strict')


if __name__ == '__main__':
    query = json.loads(sys.stdin.read())
    archive = build(query['src_dir'])
    print(json.dumps({'archive': archive, "base64sha256":get_hash(archive)}))