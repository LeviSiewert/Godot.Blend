from __future__ import annotations

from typing import Self, Iterable, Any

from .collection import CollectionKey, Collection as _Collection
from enum import Enum

class _UNSET:...

class CollectionOverlayMode(Enum):
    SUBITEM_OVERLAY_COPY = 0
    SUBITEM_PASSTHROUGH = 1

class Collection(_Collection):

    overlay : None|Collection = None
    overlay_itemmode = CollectionOverlayMode.SUBITEM_OVERLAY_COPY

    def __init__(self, key_attr, iterable = tuple(), context = None, key_is_string = True, key_resolve_incriment = False, key_formatter = None, mode:CollectionOverlayMode=CollectionOverlayMode.SUBITEM_OVERLAY_COPY, overlay:Self|None=None):
        self.overlay_itemmode = self.overlay_itemmode
        super().__init__(key_attr, iterable, context, key_is_string, key_resolve_incriment, key_formatter)
        self.set_overlay(overlay)

    def set_overlay(self, overlay:Collection|None, supress_signals:bool=False)->dict[str,tuple[Any]]:
        if self.overlay is overlay: return

        o_items = dict(self.items(use_overlay=True))

        if not (self.overlay is None):
            pass #disconnect

        self.overlay = overlay

        if not (self.overlay is None):
            pass #Connect

        if supress_signals:
            return

        n_items = dict(self.items(use_overlay=True))

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

    def overlay_chain(self, depth_first:bool=False):
        if self.overlay is None:
            yield self
            return
        if depth_first:
            yield from self.overlay.overlay_chain(depth_first=depth_first)
            yield self
        else:
            yield self
            yield from self.overlay.overlay_chain(depth_first=depth_first)

    def keys(self, use_overlay:bool=True):
        yielded : list[str] = []

        if not use_overlay:
            yield from self.data.keys()
            return

        for k in self.data.keys():
            yielded.append(k)
            yield k

        for _p in self.overlay_chain():
            for k in _p.data.keys():
                if k in yielded: 
                    continue
                yielded.append(k)
                yield k

    def values(self, use_overlay:bool=True):
        for k in self.keys(use_overlay=use_overlay):
            yield self._get(k, use_overlay=use_overlay)
        
    def items(self, use_overlay:bool=True):
        for k in self.keys(use_overlay=use_overlay):
            yield (k, self._get(k, use_overlay=use_overlay))

    def _get[D](self, key:str, default:D=_UNSET, use_overlay:bool=True, unset_ok:bool=False)->Any|D:
        """ Converts promises outgoing, unless required to return direct """
        if use_overlay:
            chain : Iterable[Self] = self.overlay_chain()
        else:
            chain : Iterable[Self] = tuple([self])


        for p in chain:
            v = p.data.get(key, _UNSET)
            if v is _UNSET:
                continue
            return v

        if (default is _UNSET) and (not unset_ok):
            raise KeyError(key)
        
        return default