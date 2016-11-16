from components import *

MEMORY_SIZE = 500

command = '''lastv1 0
lastv2 1
current 0
maxiter 0
input maxiter
_loopstart cmp maxiter
leje end
mov lastv1 @acc
add lastv2
mov @acc current
mov lastv2 lastv1
mov current lastv2
prntint @acc
mov maxiter @acc
sub #1
mov @acc maxiter
jump loopstart
_end halt'''

myprogram = Compiler(command, MEMORY_SIZE)
myprogram.compile()

mycpu = Cpu(MEMORY_SIZE, myprogram.compiled)
# Todo: add interpretation of assembly file
