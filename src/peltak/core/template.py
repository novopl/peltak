# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
import os
from os.path import abspath, basename, dirname, exists, join, isdir, relpath
from zipfile import ZipFile

try:
    # python 3
    from io import BytesIO
except ImportError:
    # python 2
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

# local imports
from peltak.core import log
from peltak.core import fs


TEMPLATE_LINE_SEP = '\n'
TEMPLATE_CONFIG_FILE = 'peltak-template-config.json'
NAME_MARKER = '_PELTAK-SCAFFOLD-NAME_'


class Scaffold(object):
    CONFIG_FILE = 'peltak-scaffold-config.json'
    NAME_MARKER = '_PELTAK-SCAFFOLD-NAME_'

    def __init__(self, name=None, zipfile=None, **kw):
        self.zipfile = zipfile or BytesIO()
        self.name = name
        self.line_sep = kw.get('line_sep', TEMPLATE_LINE_SEP)
        self.marked_files = kw.get('marked_files', [])

    @property
    def size(self):
        start_pos = self.zipfile.tell()

        self.zipfile.seek(0, os.SEEK_END)
        size = self.zipfile.tell()
        self.zipfile.seek(start_pos, os.SEEK_SET)

        return size

    @property
    def config(self):
        return {
            'name': self.name,
            'line_sep': self.line_sep,
            'marked_files': self.marked_files,
        }

    @classmethod
    def create(cls, src_dir, name, exclude):
        print("Exclude: {}".format(exclude))

        if name is None:
            name = basename(abspath(src_dir))

        log.info("Creating template ^35{}".format(name))

        marked_files = []

        sfiles = list(Scaffold._iter_files(src_dir, name, exclude))

        zipfile = BytesIO()
        with ZipFile(zipfile, 'w') as zip:
            i = 0
            for path, arc_path in Scaffold._iter_files(src_dir, name, exclude):
                content, marked = Scaffold._prepare_file(path, name)
                zip.writestr(arc_path, content)

                if marked:
                    marked_files.append(arc_path)

                i += 1
                log.info("[{:4}] Adding ^35{}", i, path)

        return Scaffold(name, zipfile, marked_files=marked_files)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as fp:
            zipfile = BytesIO(fp.read())

        with ZipFile(zipfile) as zip:
            config = json.loads(zip.read(Scaffold.CONFIG_FILE))

        return Scaffold(
            config['name'], zipfile,
            line_sep=config['line_sep'],
            marked_files=config['marked_files']
        )

    def write(self, path):
        zip_path = join(path, self.name + '.scaffold')

        with ZipFile(self.zipfile, 'a') as zip:
            zip.writestr(Scaffold.CONFIG_FILE, json.dumps(self.config))

        with open(zip_path, 'wb') as fp:
            fp.write(self.zipfile.getvalue())

    def apply(self, proj_name, out_path):
        with ZipFile(self.zipfile) as zip:
            config = json.loads(zip.read(Scaffold.CONFIG_FILE))

            for i, arc_path in enumerate(zip.namelist()):
                if arc_path == Scaffold.CONFIG_FILE:
                    continue

                file_path = join(out_path, proj_name, arc_path)

                if NAME_MARKER in arc_path:
                    file_path = file_path.replace(NAME_MARKER, proj_name)

                if not exists(dirname(file_path)):
                    os.makedirs(dirname(file_path))

                print('{:5d}] {}'.format(i, file_path))
                content = zip.read(arc_path)

                if arc_path in config['marked_files']:
                    content = content.decode('utf-8')
                    content = Scaffold._render_file(content, {
                        NAME_MARKER: proj_name
                    })

                    with open(file_path, 'w') as fp:
                        fp.write(content)
                else:
                    with open(file_path, 'wb') as fp:
                        fp.write(content)

    @staticmethod
    def _iter_files(src_dir, template_name, exclude):
        for file_name, path in fs.filtered_walk(src_dir, exclude):
            # if not isdir(path):
            arc_path = relpath(path, src_dir)
            arc_path = arc_path.replace(template_name, NAME_MARKER)

            yield path, arc_path

    @staticmethod
    def _render_file(content, values):
        lines = []

        for line in content.split(TEMPLATE_LINE_SEP):
            rendered = line

            for marker, value in values.items():
                if marker in line:
                    rendered = rendered.replace(marker, value)

            lines.append(rendered)

        return os.linesep.join(lines)

    @staticmethod
    def _prepare_file(path, template_name):
        is_marked = False
        try:
            with open(path) as fp:
                lines = []
                for i, line in enumerate(fp.readlines()):
                    line = line[:-len(os.linesep)]
                    prepped = line.replace(template_name, NAME_MARKER)

                    if template_name in line:
                        is_marked = True
                        log.cprint("{:4}| ^90{:50} ^32-> ^0{}",
                                   i, line, prepped)

                    lines.append(prepped)

                return TEMPLATE_LINE_SEP.join(lines), is_marked

        except UnicodeDecodeError:
            with open(path, 'rb') as fp:
                return fp.read(), False
