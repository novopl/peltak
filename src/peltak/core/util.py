# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


from datetime import datetime, timedelta


class CachedPropertyMeta(object):
    def __init__(self, seconds):
        self.last_update = datetime.now() - timedelta(seconds=seconds + 1)
        self.value = None


def cached_property(seconds=1):
    def decorator(fn):
        meta_attr = '__cached_{}'.format(fn.__name__)

        @property
        def prop_wrapper(self):
            meta = self.__dict__.setdefault(meta_attr,
                                            CachedPropertyMeta(seconds))
            since_update = (datetime.now() - meta.last_update).total_seconds()

            if since_update > seconds:
                meta.last_update = datetime.now()
                meta.value = fn(self)

            return meta.value

        return prop_wrapper

    return decorator
