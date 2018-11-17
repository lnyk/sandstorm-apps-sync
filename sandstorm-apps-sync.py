#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

import click
import os
import shutil
import requests
import json
from datetime import datetime
from tqdm import tqdm
from urllib.request import urlretrieve
from urllib.parse import urljoin

@click.group()
def op():
    """This script is used to clone app-index.sandstorm.io to local directory.

    Command Help:

    <script.py> COMMAND --help to see COMMAND help."""
    pass

@op.command(short_help="Sync the complete app index and files")
@click.option('--public_path', '-p', type=click.Path(exists=False),
           default='./public',
              help="Destination directory, default set to ./public/")
def sync(public_path):
    """sync is used to clone app-index.sandstorm.io to local directory.

    This command WILL REMOVE everything in ./public/ directory."""
    if os.path.exists(public_path):
        color_print("Directories already exists, remove them.", dt_bg='yellow')
        shutil.rmtree(public_path)

    APATH = os.path.join(public_path, 'apps')
    PPATH = os.path.join(public_path, 'packages')
    IPATH = os.path.join(public_path, 'images')

    BASEURL = 'https://app-index.sandstorm.io'
    color_print('Create basic directories.')
    os.makedirs(APATH)
    os.makedirs(PPATH)
    os.makedirs(IPATH)

    download(urljoin(BASEURL, 'apps/index.json'),
             os.path.join(APATH, 'index.json')
    )

    color_print('Load SandStorm App-Market index file')
    with open(os.path.join(APATH, 'index.json'), 'r') as file:
        index = json.load(file)

    for i, app in enumerate(index['apps']):
        color_print('{} {} {}'.format(
            click.style(str(i+1) + '/' + str(len(index['apps'])), fg='black', bg='white'),
            click.style(app['name'], bg='cyan'),
            click.style(app['version'], bg='green'),
        ))
        download(urljoin(BASEURL, 'apps/' + app['appId'] + '.json'),
                 os.path.join(APATH, app['appId'] + '.json'),
                 leave=False
        )
        download(urljoin(BASEURL, 'images/' + app['imageId']),
                 os.path.join(IPATH, app['imageId']),
                 leave=False
        )
        download(urljoin(BASEURL, 'packages/' + app['packageId']),
                 os.path.join(PPATH, app['packageId']),
                 leave=False
        )


    click.echo(apps_list[0])

    pass

def color_print(txt, txt_fg=None, txt_bg=None, dt_fg=None, dt_bg='cyan', blink=False, bold=False):
    click.echo('{} {}'.format(
        click.style(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fg=dt_fg, bg=dt_bg, blink=blink, bold=bold),
        click.style(txt, bg=txt_bg)
    ))

def download(url, localfile, leave=True):
    color_print('Get {}'.format(url), dt_bg='blue')
    try:
        with requests.get(url, stream=True) as r:
            # Total size in bytes.
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024*1024
            wrote = 0

            with tqdm(total = total_size,
                      unit = 'B',
                      unit_scale = True,
                      unit_divisor = 1024,
                      leave=leave
            ) as pbar:
                with open(localfile, 'wb') as f:
                    for data in r.iter_content(block_size):
                        f.write(data)
                        pbar.update(len(data))
    except:
        color_print('Cannot get {}. Exit.'.format(url), dt_bg='red', blink=True, bold=True)
        exit(1)

if __name__ == '__main__':
    op()
