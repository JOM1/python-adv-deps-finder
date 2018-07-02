import dis
import sys
import io
import re
from dill.source import getsource

def getglobals(func_name):
    this_module = sys.modules['__main__']

    stdout_ = sys.stdout #Keep track of the previous value.
    stream = io.StringIO()
    sys.stdout = stream

    dis.dis(getattr(this_module, func_name)) # prints opcodes to the stream

    sys.stdout = stdout_ # restore the previous stdout.
    opcodes = stream.getvalue()

    splited = re.split("\n", opcodes)
    globals_used = filter(lambda x: re.match(".*\sLOAD_GLOBAL\s.*", x), splited)
    globals_used = [re.search("\(\w+\)$",y).group()[1:-1] for y in globals_used]

    globals_by_type = dict()
    globals_by_type['function'] = []
    globals_by_type['other'] = []
    
    for global_var in globals_used:
        try:
            type_of = type(getattr(this_module, global_var)).__name__
            if type_of == 'function':
                globals_by_type['function'].append(global_var)
                other_globals = getglobals(global_var)
                globals_by_type['function'].extend(other_globals['function'])
                globals_by_type['other'].extend(other_globals['other'])
            else:
                globals_by_type['other'].append(global_var)
        except AttributeError:
            pass
    return globals_by_type

def line_contains_var_in_list(_line, _list):
    for var in _list:
        if re.search("[^\w]"+var+"([^\w]|)", _line):
            return True
    return False

def get_needed_source(func_name):
    needed_globals = getglobals(func_name)

    this_module = sys.modules['__main__']
    full_source_lines = re.split("\n", getsource(this_module))
    all_imports = list(filter(lambda x: re.search("\s?import\s", x), full_source_lines))
    
    needed_imports = []
    for imp in all_imports:
       if line_contains_var_in_list(imp, needed_globals['other']):
           needed_imports.append(imp)

    imported_funcs = []
    for func in needed_globals['function']:
        for imp in all_imports:
            if re.search("[^\w]"+func+"([^\w]|)", imp):
                needed_imports.append(imp)
                imported_funcs.append(func)
                break
    unimported_funcs = [func for func in
                         needed_globals['function'] if
                          func not in imported_funcs]
    
    needed_source = ""

    for imp in needed_imports:
        needed_source += imp + "\n"

    needed_source += "\n" + getsource(getattr(this_module, func_name)) + "\n"

    for func in unimported_funcs:
        needed_source += getsource(getattr(this_module, func)) + "\n"
    
    return needed_source

if __name__ != '__main__':
    exit()

from sys import modules

def a():
    getsource(b)
    sys.modules['__main__'].__dict__
def b():
    modules['__main__']
    f()
def f():
    print('a')
    re.match("","")
    pass


print(get_needed_source('a'))
