#!/usr/bin/python3
#
# Copyright (c) 2018 Evan Klitzke <evan@eklitzke.org>
#
# This file is part of gh-mirror.
#
# gh-mirror is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# gh-mirror is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# gh-mirror. If not, see <http://www.gnu.org/licenses/>.

import argparse
import json
import os
import urllib.request
import urllib.parse
import subprocess


def get_repos(username: str, page=None, per_page=100, out=None):
    if out is None:
        out = []
    path = 'https://api.github.com/users/{}/repos'.format(username)
    kw = {'per_page': 100}
    if page is not None:
        kw['page'] = page
        next_page = page + 1
    else:
        next_page = 2
    query = urllib.parse.urlencode(kw)
    with urllib.request.urlopen('{}?{}'.format(path, query)) as resp:
        body = resp.read()
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        data = json.loads(body)
        if not data:
            return out
        out.extend(data)
        return get_repos(username, next_page, per_page=per_page, out=out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--destdir', help='Destination dir')
    parser.add_argument('username')
    args = parser.parse_args()

    for repo in get_repos(args.username):
        dest = os.path.join(args.destdir, repo['name'])
        try:
            if not os.path.exists(dest):
                print('clone {}'.format(repo['full_name']))
                url = 'https://github.com/{}'.format(repo['full_name'])
                subprocess.check_call(
                    ['git', 'clone', '--quiet', '--bare', url, dest])
            else:
                print('fetch {}'.format(repo['full_name']))
                os.chdir(dest)
                subprocess.check_call(['git', 'fetch', '--all', '--quiet'])
        except subprocess.CalledProcessError:
            print('ERROR {}'.format(repo['full_name']))


if __name__ == '__main__':
    main()
