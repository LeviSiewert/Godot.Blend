from __future__ import annotations

from typing import Type

from .transformer import Transformer, TransformerRuleset, TransformerModule
from .structure import Properties, Project, Resource, Node
from .structure_promise import StructReference
from .signals import Signal

N = Properties|Project|Resource|Node|Signal

def copy(node:N): raise NotImplementedError()
def deepcopy(node:N): raise NotImplementedError()
def check_recursion(node:N): raise NotImplementedError()
def singulate(node:N): raise NotImplementedError()
def localize(node:N): raise NotImplementedError()
def format_extresources(node:N): raise NotImplementedError()


def normalize(node           : N,
            /, 
            singulate        : bool = False, 
            localize         : bool = True,
            instanciate_load : bool = False,
            fix_instanciate  : bool = True,
            check_recursion  : bool = True, 
            in_place         : bool = True, 
            scope            : Type = None,
            )->N: 
        ''' 
        :param singulate: 
        Ensures that every node that is referenced in multiple scopes is copied into those scopes (w/a)
        - IE: (R1.subresources["sr1"] is R2.subresources["sr1"]) ->> (R1.subresources["sr1"] == R2.subresources["sr1_copy"])
        :param localize:
        Ensures that every referenced node that *doesn't* exist in the scope is placed within that scope
        - IE: 
            - (R1.subresources["sr1"].properties["ref"] is sr2(free)) ->> (R1.subresources["sr1"].properties["ref"] -> R1.subresources["sr2"])
            - (R1.subresources["sr1"].properties["ref"] is R2(Free)   ->> (R1.subresources["sr1"].properties["ref"] -> R1.ExtResources[...] -> P.Resources["R2"] is R2)
        - Copies to local w/ singulate w/a
        :param instanciate_load:
        Ensures that all instances referenced are loaded
        - IE 
            - (R1.instance is StructRef(R0)) ->> (R1.instance is R0)
        If project is not set, an error will occur
        :param fix_instanciate: 
        Ensures that any instanciate structure is fully initialized
        - IE 
            - (R1.instance is R0 && R1.overlay is None) ->> (R1.instance is R0 && R1.overlay is R0, R1.nodes...ect...)
        :param check_recursion:
        Checks that recursion rules within the godot structure are not broken;
        OK:
            Node <-> Node (As ref via nodepath)
        NOT_OK:
            Sr1 <-> Sr2 (Same scope)
            R1 -> R2 -> R1
        #TODO: Double check recurision & co-dependency rules.

        :param in_place:
        Manipulate tree in place, or return a deepcopy. 
        A deepcopy will *not* be attached to a project/outer scope;
            - a copy will not exist in outer scopes collections
            - a copy will not have the context extended from the parent
        Typically only used in exports

        :param scope:
        Limitiation in lateral action, usually set by first node's type.
        - IE 
            - R1.normalize(in_place=False, localize=True) ; where (R1.p["ref"]->R2) ; R2 is not coppied, but is localized w/a 
        '''
        
        raise NotImplementedError()
    