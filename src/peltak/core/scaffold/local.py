# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# stdlib imports
import os
from os.path import expanduser, exists, join

# 3rd party imports
from cached_property import cached_property_ttl

# local imports
from peltak.core import log
from .scaffold import Scaffold


class LocalStore(object):
    DEFAULT_PATH = expanduser('~/.config/peltak/local')

    def __init__(self, path=None):
        self.path = path or LocalStore.DEFAULT_PATH
        if not exists(self.path):
            os.makedirs(self.path)

    @cached_property_ttl(ttl=5)
    def scaffolds(self):
        scaffolds = []
        for filename in os.listdir(self.path):
            if filename.endswith(Scaffold.FILE_EXT):
                try:
                    path = join(self.path, filename)
                    scaffold = Scaffold.load_from_file(path)

                    scaffolds.append(scaffold)
                except Scaffold.Invalid:
                    pass

        return scaffolds

    def add(self, scaffold):
        scaffold.write(self.path)

        self._invalidate_cache()

    def delete(self, name):
        scaffold = self.load(name)

        if scaffold is not None:
            os.remove(scaffold.path)
            self._invalidate_cache()

        else:
            log.err("'{}' does not exist".format(name))

    def load(self, name):
        return next((x for x in self.scaffolds if x.name == name), None)

    def push(self, name):
        raise NotImplemented("Remote service is not yet implemented")

    def pull(self, name):
        raise NotImplemented("Remote service is not yet implemented")

    def _invalidate_cache(self):
        if 'scaffolds' in self.__dict__:
            del self.__dict__['scaffolds']
