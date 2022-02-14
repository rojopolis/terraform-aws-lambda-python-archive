
from distutils.dir_util import copy_tree

import base64
import errno
import hashlib
import json
import logging
import os
import subprocess
import sys
import tempfile
from typing import List
import zipfile

logger = logging.getLogger()

def build(src_dir: str, output_path: str, install_dependencies: bool, exclude_files: List[str] = []) -> str:
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
                 *(['--no-deps'] if install_dependencies == 'false' else [])],
                 check=True,
                 stdout=subprocess.DEVNULL,
            )
        make_archive(build_dir, output_path, exclude_files)
        return output_path

def make_archive(src_dir: str, output_path: str, exclude_files: List[str] = []) -> None:
    '''
    Create an archive at the designated location.
    '''
    try:
        os.makedirs(os.path.dirname(output_path))
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    with zipfile.ZipFile(output_path, 'w') as archive:
        for root, dirs, files in os.walk(src_dir):
            
            for file in files:
                is_pyc = file.endswith('.pyc')
                is_distinfo = '.dist-info' in root
                is_ignored = file in exclude_files

                if is_pyc or is_distinfo or is_ignored:
                    logger.info('Skipping {r}/{f}'.format(
                        r=root,
                        f=file
                    ))
                    break
                metadata = zipfile.ZipInfo(
                    os.path.join(root, file).replace(src_dir, '').lstrip(os.sep)
                )
                metadata.external_attr = 0o755 << 16
                with open(os.path.join(root, file), 'rb') as f:
                    data = f.read()
                archive.writestr(
                    metadata,
                    data
                )

def get_hash(output_path: str) -> str:
    '''
    Return base64 encoded sha256 hash of archive file
    '''
    with open(output_path, 'rb') as f:
        h = hashlib.sha256()
        h.update(f.read())
    return base64.standard_b64encode(h.digest()).decode('utf-8', 'strict')

if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    query = {
        'src_dir': 'examples/python/',
        'output_path': 'example_output/example.zip',
        'install_dependencies': True,
        'exclude_files': []
    }
    # query = json.loads(sys.stdin.read())
    logging.debug(query)
    archive = build(
        src_dir=query['src_dir'], 
        output_path=query['output_path'], 
        install_dependencies=query['install_dependencies'], 
        exclude_files=query['exclude_files'])
    print(json.dumps({'archive': archive, 'base64sha256':get_hash(archive)}))
