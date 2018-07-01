import dis
import sys
import io
import re

def a():
    b()
    sys.modules['__main__'].__dict__
def b():
    pass

stdout_ = sys.stdout #Keep track of the previous value.
stream = io.StringIO()
sys.stdout = stream
dis.dis(a) # Here you can do whatever you want, import module1, call test
sys.stdout = stdout_ # restore the previous stdout.
variable = stream.getvalue()  # This will get the "hello" string inside the variable
splited = re.split("\n", variable)
globals_used = filter(lambda x: re.match(".*\sLOAD_GLOBAL\s.*", x), splited)
for y in globals_used:
    print(re.search("\(\w+\)$",y).group()[1:-1])