import sys


# file open check
def checkArgv():
    if len(sys.argv) == 1:
        print ('Please set asm filename')
        exit()
    elif len(sys.argv) >= 3:
        print ('Please only set 1 argument for asm filename')
        exit()

# read file
def readAsmFile(filepath):
    f = open(filepath, 'r')
    lines = f.readlines()
    f.close()
    return lines

# read line by line
def readAsmLine(line):
    # check comment line
    if line[0] == '.': # this is comment line
        return ['.', '.', '.']

    # initialization
    line_split = line.split()
    line_label = ''
    line_opcode = ''
    line_operand = ''

    if len(line_split) == 2:
        line_opcode, line_operand = line_split
    elif len(line_split) == 3:
        line_label, line_opcode, line_operand = line_split
    elif len(line_split) == 1:
        line_opcode = line_split[0]

    return [line_label, line_opcode, line_operand]

# main
def main():
    checkArgv()

    # Initialization
    intermediate_file = []
    # Dictionary of defined symbols and their values
    SYMTAB = {}
    # OP Table
    OPTAB = {'START':'', 'LDA':0x00, 'STA':0x0C, 'ADD':0x18, 'RSUB':0x4C}

    #--------------- Pass 1 ---------------
    LOCCTR = 0
    lines = readAsmFile(sys.argv[1])
    for line in lines:
        line_label, line_opcode, line_operand = readAsmLine(line)

        if line_opcode == 'START':
            start_addr = int(line_operand)
            LOCCTR = start_addr
            intermediate_file.append(['', line_label, line_opcode, line_operand])
        elif line_opcode != 'END':
            if not line_label == '.': # if this line is not a comment line
                if not line_label == '': # there is a symbol in label field
                    if line_label in SYMTAB: # search SYMTAB, if found
                        print ('ERROR: duplicated symbol')
                        exit()
                    else:
                        SYMTAB[line_label] = LOCCTR # insert (LABEL, LOCCTR) into SYMTAB

                # write line to intermediate file
                intermediate_file.append([LOCCTR, line_label, line_opcode, line_operand])

            if line_opcode in OPTAB: # search OPTAB for OPCODE
                LOCCTR += 3
            elif line_opcode == 'WORD':
                LOCCTR += 3
            elif line_opcode == 'RESW':
                LOCCTR += 3*int(line_operand)
            elif line_opcode == 'RESB':
                LOCCTR += int(line_operand)
            elif line_opcode == 'BYTE':
                print ('implement later')
            elif line_opcode == '.':
                print ('')
            else:
                print ('ERROR: invalid operation code')
                exit()
    program_length = LOCCTR - start_addr

    print ('program length is {:d}'.format(program_length))
    print (SYMTAB.items())
    for line in intermediate_file:
        print (line)

    #--------------- Pass 2 ---------------
    for line in intermediate_file: # read first input line (from intermediate_file)
        objectCode = ""
        line_addr = line[0] # PC는 +3 위치
        line_label = line[1] # pass2에서는 의미없음
        line_opcode = line[2] # read line opcode
        line_operand = line[3] # 즉시값 혹은 SYMBOL
        ni = ["0", "0"]
        xbpe = ["0", "0", "0", "0"]
        display = "0x000" # 12 bits

        if line_opcode == 'START': # if OPCODE == 'START' then
            print('')
            # read next input line
        elif line_opcode != 'END':
            if line_label != ".":
                if line_opcode in OPTAB.keys():
                    if line_operand != "": # operand가 비워져 있지 않고, 즉시값이 아니면
                        if line_operand in SYMTAB.keys(): # STMTAB에 있으면,
                            ni[0] = "1"
                            ni[1] = "1"
                            xbpe[2] = "1" # PC flag 설정
                            PC = int(line_addr) + 3 # 현재 PC 값
                            display = "{:03x}".format((int(SYMTAB[line_operand]) - PC)) # 떨어진 byte
                            objectCode = "{:02x}".format(OPTAB[line_opcode] + int("".join(ni), 2)) \
                                         + "{:01x}".format(int("".join(xbpe), 2)) + display
                        elif line_operand[0] == "#":  # 즉시 값이라면
                            ni[0] = "0"  # 플래그 설정
                            ni[1] = "1"
                            display = "{:03x}".format(int(line_operand[1:]))
                            objectCode = "{:02x}".format(OPTAB[line_opcode] + int("".join(ni), 2)) \
                                         + "{:01x}".format(int("".join(xbpe), 2)) + display
                        else:
                            print("error! (undefined symbol)")
                            break
                    else: #RSUB 처리
                        objectCode = "{:02x}".format(OPTAB[line_opcode] + int("11", 2)) + "0000"

                elif line_opcode in ["BYTE", "WORD"]: # BYTE 처리
                    objectCode = "{:06x}".format(int(line_operand))
                elif line_opcode == "RSUB": # RSUB은 예외처리
                    continue
                else:
                    pass
                if objectCode != "":
                    print("0x{:03x} {:s}".format(line_addr, objectCode))



main()