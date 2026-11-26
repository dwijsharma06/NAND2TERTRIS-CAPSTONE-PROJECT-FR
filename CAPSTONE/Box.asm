// Box program for roll number ending in 83
// Starts at screen row 83, is 20 rows high and 64 pixels (4 words) wide.
// Draws black while a key is pressed; clears the box when no key is pressed.

(LOOP)
    @KBD
    D=M
    @SETBLACK
    D;JGT

    @R12
    M=0
    @PAINT
    0;JMP

(SETBLACK)
    @R12
    M=-1

(PAINT)
    @19040
    D=A
    @R13
    M=D

    @20
    D=A
    @R14
    M=D

(ROW)
    @4
    D=A
    @R15
    M=D

(COL)
    @R12
    D=M
    @R13
    A=M
    M=D

    @R13
    M=M+1

    @R15
    MD=M-1
    @COL
    D;JGT

    @28
    D=A
    @R13
    M=D+M

    @R14
    MD=M-1
    @ROW
    D;JGT

    @LOOP
    0;JMP
