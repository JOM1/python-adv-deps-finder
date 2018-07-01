import dis
import sys
import io
import re
from dill.source import getsource

def a():
    b()
    sys.modules['__main__'].__dict__
def b():
    f()
def f():
    re.match("","")
    pass



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
    globals_by_type['module'] = []
    
    for global_var in globals_used:
        type_of = type(getattr(this_module, global_var)).__name__
        if type_of == 'function':
            globals_by_type['function'].append(global_var)
            other_globals = getglobals(global_var)
            globals_by_type['function'].extend(other_globals['function'])
            globals_by_type['module'].extend(other_globals['module'])
        elif type_of == 'module':
            globals_by_type['module'].append(global_var)
    return globals_by_type


preprocess_name = 'a'

def line_contains_var_in_list(_line, _list):
    for var in _list:
        if re.search(var, _line):
            return True
    return False

def get_needed_source(func_name):
    needed_globals = getglobals(preprocess_name)

    this_module = sys.modules['__main__']
    full_source_lines = re.split("\n", getsource(this_module))
    all_imports = filter(lambda x: re.match("\s?import\s", x), full_source_lines)
    
    needed_imports = filter(lambda x: line_contains_var_in_list(x,
                                        needed_globals['module']), all_imports)
    
    needed_source = ""

    for imp in needed_imports:
        needed_source += imp + "\n"

    needed_source += "\n" + getsource(getattr(this_module, func_name)) + "\n"

    for func in needed_globals['function']:
        needed_source += getsource(getattr(this_module, func)) + "\n"
    
    return needed_source

print(get_needed_source(preprocess_name))