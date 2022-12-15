
from distutils.dir_util import copy_tree

import base64
import errno
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

def build(src_dir, output_path, install_dependencies, is_layer):
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
                 '-r', os.path.join(build_dir, 'requirements.txt'),
                 *([] if install_dependencies else ['--no-deps'])],
                 check=True,
                 stdout=subprocess.DEVNULL,
            )
        make_archive(build_dir, output_path, is_layer)
        return output_path


def make_archive(src_dir, output_path, is_layer):
    try:
        os.makedirs(os.path.dirname(output_path))
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    dir_with_files = {
        dir: sorted(files)
        for dir, _, files in os.walk(src_dir)
    }

    with zipfile.ZipFile(output_path, 'w') as archive:
        for dir in sorted(dir_with_files.keys()):
            for file in dir_with_files[dir]:
                if file.endswith('.pyc'):
                    continue
                metadata = zipfile.ZipInfo(
                    os.path.join(
                        'python' if is_layer else '',
                        dir.replace(src_dir, '').lstrip(os.sep),
                        file
                    )
                )
                metadata.external_attr = 0o755 << 16
                with open(os.path.join(dir, file), 'rb') as f:
                    data = f.read()
                archive.writestr(
                    metadata,
                    data
                )

def get_hash(output_path):
    '''
    Return base64 encoded sha256 hash of archive file
    '''
    with open(output_path, 'rb') as f:
        h = hashlib.sha256()
        h.update(f.read())
    return base64.standard_b64encode(h.digest()).decode('utf-8', 'strict')


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    query = json.loads(sys.stdin.read())
    logging.debug(query)
    archive = build(
        query['src_dir'],
        query['output_path'],
        query['install_dependencies'] == 'true',
        query['is_layer']  == 'true'
    )
    print(json.dumps({'archive': archive, 'base64sha256':get_hash(archive)}))
