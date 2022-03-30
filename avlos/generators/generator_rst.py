
from rstcloth import RstCloth


def process(instance, config):    

    d = RstCloth()
    state = {"ep_counter": 1}
    
    traverse(instance, state, d)
    d.write(config["output_file"])
    # d.title('Example Use')
    # d.newline()
    # d.h2('Contents')
    # d.directive(name="contents", fields=[('local', ''), ('backlinks', 'None')])
    # d.newline()
    # d.h2('Code -- shebang')
    # d.codeblock('#!/usr/bin/env')

    # d.print_content()


def traverse(obj, state, d):
    try:
        for child in obj.children.values():
            traverse(child, state, d)
    except AttributeError:
        d.newline()
        d.h2(obj.name)