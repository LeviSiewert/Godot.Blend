from __future__ import annotations

from typing import Self

from .collection import CollectionKey, Collection as _Collection
from enum import Enum

class CollectionOverlayMode(Enum):
    SUBITEM_OVERLAY_COPY = 0
    SUBITEM_PASSTHROUGH = 1

class Collection(_Collection):

    overlay : None|Collection = None
    overlay_itemmode = CollectionOverlayMode.SUBITEM_OVERLAY_COPY

    def __init__(self, key_attr, iterable = ..., context = None, key_is_string = True, key_resolve_incriment = False, key_formatter = None, mode:CollectionOverlayMode=CollectionOverlayMode.SUBITEM_OVERLAY_COPY, overlay:Self|None=None):
        self.overlay_itemmode = self.overlay_itemmode
        super().__init__(key_attr, iterable, context, key_is_string, key_resolve_incriment, key_formatter)
        self.set_overlay(overlay)

    def set_overlay(self, overlay:Collection|None, supress_signals:bool=False)->dict[str,tuple[Any]]:
        if self.overlay is overlay: return

        o_items = dict(self.items(include_overlay=True))

        if not (self.overlay is None):
            pass #disconnect

        self.overlay = overlay

        if not (self.overlay is None):
            pass #Connect

        if supress_signals:
            return

        n_items = dict(self.items(include_overlay=True))

        added = {k:v for k,v in n_items.items() if (not (k in o_items.keys()))}
        removed = {k:v for k,v in o_items.items() if (not (k in n_items.keys()))}
        updated = {k:(o_items[k],v) for k,v in n_items.items() if (k not in added.keys()) and (not (o_items[k] is n_items[k]))}

        for k,v in added.items():
            self.appended(k, v)
        for k,v in removed.items():
            self.removed(k, v)
        for k,(v0,v) in updated.items():
            self.replaced(k,v0, v)

        return {"add":tuple(added.values()), "removed":tuple(removed.values()), "update":tuple(updated.values())}
