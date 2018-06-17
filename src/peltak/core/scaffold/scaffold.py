# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import json
import os
import sys
from datetime import datetime
from os.path import join, isdir, relpath
from zipfile import BadZipFile, ZipFile, ZipInfo

try:
    # python 3
    from io import BytesIO
except ImportError:
    # python 2
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO


from six import string_types

# local imports
from peltak.core import log
from peltak.core import fs


TEMPLATE_CONFIG_FILE = 'peltak-template-config.json'

def marker_tag(marker):
    return '_PELTAK-SCAFFOLD-{}_'.format(marker.upper())


class Scaffold(object):
    LINE_SEP = '\n'
    FILE_EXT = '.scaffold'
    CONFIG_FILE = 'peltak-scaffold-config.json'
    TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    NAME_MARKER = marker_tag('name')

    class Invalid(RuntimeError):
        pass

    def __init__(self, zipfile, **config):
        self.zipfile = zipfile or BytesIO()
        self.config = config
        self.path = None    # Only set if loaded from file or after it's written

        self.config.setdefault('line_sep', Scaffold.LINE_SEP)
        self.config.setdefault('marked_files', [])
        self.config.setdefault('created', datetime.utcnow())
        self.config.setdefault('time_format', Scaffold.TIME_FORMAT)

        if isinstance(self.created, string_types):
            created = datetime.strptime(self.created, self.time_format)
            self.config['created'] = created

    @property
    def name(self):
        return self.config['name']

    @property
    def marked_files(self):
        return self.config['marked_files']

    @property
    def created(self):
        return self.config['created']

    @property
    def pretty_created(self):
        return self.created.strftime(Scaffold.TIME_FORMAT)

    @property
    def time_format(self):
        return self.config['time_format']

    @property
    def size(self):
        start_pos = self.zipfile.tell()

        self.zipfile.seek(0, os.SEEK_END)
        size = self.zipfile.tell()
        self.zipfile.seek(start_pos, os.SEEK_SET)

        return size

    @property
    def json_config(self):
        conf = dict(self.config)
        conf['created'] = self.created.strftime(self.time_format)
        return conf

    @property
    def files(self):
        with ZipFile(self.zipfile) as zip:
            return zip.namelist()

    @classmethod
    def create(cls, src_dir, name, exclude, markers):

        marked_files = []

        zipfile = BytesIO()
        with ZipFile(zipfile, 'w') as zip:
            i = 0
            for path, arc_path in Scaffold._iter_files(src_dir, markers, exclude):
                if isdir(path):
                    # Non-empty dirs will be added through files they contain
                    marked = False
                    # if os.listdir(path) == []:
                    zip.writestr(ZipInfo(arc_path + '/'), '')
                else:
                    content, marked = Scaffold._prepare_file(path, markers)
                    zip.writestr(arc_path, content)

                if marked:
                    marked_files.append(arc_path)

                i += 1
                log.info("[{:4}] Adding ^35{}", i, path)

        return Scaffold(zipfile, name=name, marked_files=marked_files)

    @classmethod
    def load_from_file(cls, path):
        with open(path, 'rb') as fp:
            zipfile = BytesIO(fp.read())

        try:
            with ZipFile(zipfile) as zip:
                config = json.loads(zip.read(Scaffold.CONFIG_FILE))
        except BadZipFile as ex:
            raise Scaffold.Invalid(str(ex))

        scaffold = Scaffold(zipfile, **config)
        scaffold.path = path

        return scaffold

    def write(self, path):
        zip_path = join(path, self.name + Scaffold.FILE_EXT)

        with ZipFile(self.zipfile, 'a') as zip:
            zip.writestr(Scaffold.CONFIG_FILE, json.dumps(self.json_config))

        with open(zip_path, 'wb') as fp:
            fp.write(self.zipfile.getvalue())

        self.path = zip_path

    def apply(self, proj_name, out_path):
        with ZipFile(self.zipfile) as zip:
            config = json.loads(zip.read(Scaffold.CONFIG_FILE))

            proj_path = join(out_path, proj_name)
            os.makedirs(proj_path)

            for i, arc_path in enumerate(zip.namelist()):
                if arc_path == Scaffold.CONFIG_FILE:
                    continue

                file_path = join(proj_path, arc_path)

                if Scaffold.NAME_MARKER in arc_path:
                    file_path = file_path.replace(Scaffold.NAME_MARKER,
                                                  proj_name)

                content = zip.read(arc_path)

                if arc_path in config['marked_files']:
                    content = content.decode('utf-8')
                    content = Scaffold._render_file(content, {
                        'name': proj_name
                    })

                    with open(file_path, 'w') as fp:
                        log.cprint("^0[ Template ] ^0^90{}^0", file_path)
                        fp.write(content)
                else:
                    if self._is_dir(zip, arc_path):
                        log.cprint("^34[    Dir   ] ^90{}^0", file_path)
                        os.mkdir(file_path)
                    else:
                        log.cprint("^90[   File   ] ^90{}^0", file_path)
                        with open(file_path, 'wb') as fp:
                            fp.write(content)

    @staticmethod
    def _iter_files(src_dir, markers, exclude):
        for file_name, path in fs.filtered_walk(src_dir, exclude):
            arc_path = relpath(path, src_dir)
            arc_path, _ = Scaffold._prep_line(arc_path, markers)
            # arc_path = arc_path.replace(template_name, Scaffold.NAME_MARKER)

            yield path, arc_path

    @staticmethod
    def _prepare_file(path, markers):
        is_marked = False
        try:
            with open(path) as fp:
                lines = []
                for i, line in enumerate(fp.readlines()):
                    line = line[:-len(os.linesep)]
                    prepped, marked = Scaffold._prep_line(line, markers)

                    if marked:
                        is_marked = True

                    lines.append(prepped)

                return Scaffold.LINE_SEP.join(lines), is_marked

        except UnicodeDecodeError:
            with open(path, 'rb') as fp:
                return fp.read(), False

    @staticmethod
    def _prep_line(line, markers):
        prepped = line
        is_marked = False

        for marker, value in markers.items():
            if isinstance(value, string_types):
                if value in line:
                    prepped = line.replace(value, marker_tag(marker))
                    is_marked = True
            else:
                # Multiple values for marker
                for item in value:
                    if item in line:
                        prepped = line.replace(item, marker_tag(marker))
                        is_marked = True

        return prepped, is_marked

    @staticmethod
    def _render_file(content, values):
        lines = []

        for line in content.split(Scaffold.LINE_SEP):
            rendered = line

            for marker, value in values.items():
                tag = marker_tag(marker)
                if tag in line:
                    rendered = rendered.replace(tag, value)

            lines.append(rendered)

        return os.linesep.join(lines)

    def _is_dir(self, zip, arc_path):
        zip_info = zip.getinfo(arc_path)
        if sys.version_info >= (3, 6):
            return zip_info.is_dir()
        else:
            return zip_info.filename.endswith('/')


