SET 1 r1
SET 0 r7
SET 4 r2
MOV r7 r3
ADD r1 r7 r7
#comment is counted and assembled to No-op
MOV r3 r1
;comment is skipped
SUB r2 r1 r2
BRH 5 00 0
;basicaly a halt
JMP 0 1
