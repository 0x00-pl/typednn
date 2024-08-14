import typing



A = typing.TypeVar('A')

def dot(
        vx: arr(A, lx: uint)
mw: mat(B, lx:uint, ly: uint),
fmul: (A->B->C),
fsum: (arr(C, lx:uint)->D)
)->arr(C, ly: uint)
