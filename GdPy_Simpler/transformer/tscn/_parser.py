from lark import Lark

from .resources import grammar

def make_parser(key:str="start")->Lark:
    # TODO: Figure out if I can "stream" through a secondary tranformer or customization on lark
    # Would improve memory performance a lot 
    return Lark(grammar, start=key, maybe_placeholders=True) #, parser='lalr')

file_parser = make_parser()