# -*-coding:UTF-8-*-

import sys
import collections
# To prevert the conflict
if sys.version_info.major > 2:
    from builtins import id as object_id
else:
    from __builtin__ import id as object_id

# VM setting
STACK_MAX_SIZE = 128
MEMORY_MAX_SIZE = 1024

# VM composition
stack = [None] * STACK_MAX_SIZE  # stack
memory = [None] * MEMORY_MAX_SIZE  # memory
sp = 0  # stack pointer
ax = None  # register

# VM supported inareuctions
instruction = ['LEA', 'IMM', 'JMP', 'CALL', 'JZ', 'JNZ', 'ENT', 'ADJ', 'LI',
    'LC', 'SI', 'SC', 'PUSH', 'OR', 'XOR', 'AND', 'EQ', 'NE', 'LT', 'GT','LE',
    'GE', 'SHL', 'SHR', 'ADD', 'SUB','MUL', 'DIV','MOD', 'OPEN', 'READ','CLOS',
    'PRTF', 'MALC', 'MSET', 'MCMP', 'EXIT']

# lexer and parser
# Maybe choose stack ??
# IL_MAX_SIZE = 512
# IL = [None] * IL_MAX_SIZE
# IL_ptr = 0  # IL pointer
IL = []  # Intermediate language
token = None  # token in lexer
token_val = None  # token value
string = ''  # parse string
ptr = 0  # pointer which is pointing in program text
line = 0  # program line
buffer = None  # store the program text
length = 0  # length of buffer

# token's tag
class Tag(object):
    __slots__ = ('Num', 'Fun', 'Sys', 'Glo', 'Loc', 'Id', 'Char', 'Else', 'Enum',
        'If', 'Int', 'Return','Sizeof', 'While','Assign', 'Cond', 'Lor', 'Lan',
        'Or', 'Xor', 'And', 'Eq', 'Ne', 'Lt', 'Gt', 'Le', 'Ge', 'Shl', 'Shr',
        'Add', 'Sub', 'Mul', 'Div', 'Mod', 'Inc', 'Dec', 'Brak')
    Num = 128
    Fun = 129
    Sys = 130
    Glo = 131
    Loc = 132
    Id = 133
    Char = 134
    Else = 135
    Enum = 136
    If = 137
    Int = 138
    Return = 139
    Sizeof = 140
    While = 141
    Assign = 142
    Cond = 143
    Lor = 144
    Lan = 145
    Or = 146
    Xor = 147
    And = 148
    Eq = 149
    Ne = 150
    Lt = 151
    Gt = 152
    Le = 153
    Ge = 154
    Shl = 155
    Shr = 156
    Add = 157
    Sub = 159
    Mul = 160
    Div = 161
    Mod = 162
    Inc = 163
    Dec = 164
    Brak = 165

# symbol type
symbol_type = collections.namedtuple('symbol_type', ['Token', 'Name', 'Class', 'Type', 'Value'])

# an Env's instance store current scope and its father scope
class Env(object):

    def __init__(self, pre=None):
        self.table = dict()
        self.pre = pre

    def put(self, name, symbol):
        self.table[name] = symbol

    def get(self, name):
        env = self
        while env is not None:
            if name in env.table:
                return True
            env = env.pre
        return False

env_tree = Env()

# C Data Type
class Type(object):
    CHAR = 0
    INT = 1
    DOUBLE = 2
    PTR = 3

expr_type = None

# Syntax Exception
class SyntaxException(Exception):

    def __init__(self, msg='invalid syntax'):
        self.msg = msg

    def __str__(self):
        return 'SyntaxError: {0}'.format(self.msg)

# match the token
def match(tk):
    if token == tk:
        next()
    else:
        raise SyntaxException

def expression(level):
    id = None
    tmp = None
    addr = None
    global expr_type

    if not token:
        raise Exception
        sys.exit()

    if token == Tag.Num:
        match(Tag.Num)
        IL.append('IMM')
        IL.append(token_val)
        expr_type = Type.INT
    elif token == '"':
        IL.append('IMM')
        IL.append = token_val
        match('"')
        while token == '"':
            match('"')
            while token == '"':
                match('"')
        # data ??
        #
        # What the fuck
        #
        expr_type = Type.PTR
    elif token == Tag.Sizeof:
        # support sizeof(variable)
        match(Tag.Sizeof)
        match('(')

        if token == Tag.INT:
            match(Tag.INT)
            expr_type = Type.INT
        elif token == Tag.Char:
            match(Tag.Char)
            expr_type = Type.CHAR

        while token == Tag.Mul:
            match(Tag.Mul)
            # expr_type =
        match(')')

        IL.append('IMM')
        # CHAR 1 byte
        # INT 4 byte
        IL.append(1 if expr_type == Type.CHAR else 4)
    elif token == Tag.Id:
        match(Id)
        id = current_id
        if token == '(':
            match('(')
            tmp = 0
            # parse the arguments
            while token != ')':
                expression(Assign)
                IL.append('PUSH')
                tmp += 1
                if token == ',':
                    match(',')
            match(')')

            if id.Class == Tag.Sys:
                IL.append(id.Value)
            elif id.Class == Tag.Fun:
                IL.append('CALL')
                IL.append(id.Value)
            else:
                raise SyntaxException('illegal function')
                sys.exit()

            # important !!!
            if tmp > 0:
                IL.append('ADJ')
                IL.append(tmp)
            expr_type = id.Type
        elif id.Class == Tag.Num:
            IL.append('IMM')
            IL.append(id.Value)
            expr_type = Type.INT
        else:
            if id.Class == Tag.Loc:
                IL.append('LEA')
                IL.append(index_of_bp - id.Value)
            else:
                pass
    elif token == '(':
        match('(')
        if token == Tag.Int or token == Tag.Char:
            tmp = Type.CHAR if token == Tag.Char else Type.INT
            match(token)
            while token == Tag.Mul:
               match(Tag.Mul)
               tmp = tmp + Type.PTR
            match(')')
            expression(Tag.Inc)
            expression(Tag.Inc)
        else:
            expression(Tag.Assign)
            match(')')
    elif token == Tag.Mul:
        match(Tag.Mul)
        expression(Tag.Inc)
        if expr_type >= Type.PTR:
            expr_type = expr_type - Type.PTR
        else:
            raise SyntaxException('illegal dereference')
            sys.exit()
        IL.append('LC' if expr_type == Type.CHAR else 'LI')
    elif token == Tag.And:
        match(Tag.And)
        expression(Tag.Inc)
        if IL[-1] == 'LC' or IL[-1] == 'LI':
            IL.pop()
        else:
            raise SyntaxException('illegal address')
            sys.exit()
        expr_type = expr_type + Type.PTR
    elif token == '!':
        match('!')
        expression(Tag.Inc)
        IL.append('PUSH')
        IL.append('IMM')
        IL.append(0)
        IL.append('EQ')
        expr_type = Type.INT
    elif token == '~':
        match('~')
        expression(Tag.Inc)
        IL.append('PUSH')
        IL.append('IMM')
        IL.append(-1)
        IL.append('XOR')
        expr_type = Type.INT
    elif token == Tag.Add:
        match(Tag.Add)
        expression(Tag.Inc)
        expr_type = Type.INT
    elif token == Tag.Sub:
        match(Tag.Sub)
        if token == Tag.Num:
            IL.append('IMM')
            IL.append(-token_val)
            match(Tag.Num)
        else:
            IL.append('IMM')
            IL.append(-1)
            IL.append('PUSH')
            expression(Tag.Inc)
            IL.append('MUL')
        expr_type = Type.INT
    elif token == Tag.Inc  or token == Tag.Dec:
        tmp = token
        match(token)
        expression(Tag.Inc)
        if IL[-1] == 'LC':
            IL[-1] = 'PUSH'
            IL.append('LC')
        elif IL[-1] == 'LI':
            IL[-1] = 'PUSH'
            IL.append('LI')
        else;
            raise Exception
            sys.exit()
        IL.append('PUSH')
        IL.append('IMM')
        IL.append(4 if expr_type > Type.PTR else 1)
        IL.append('ADD' if tmp == Tag.Inc else 'SUB')
        IL.append('SC' if expr_type == Type.CHAR else 'SI')
    else:
        raise Exception
        sys.exit()

    # ---------------------------
    while token >= level:
        tmp = expr_type
        if token == Tag.Assign:
            match(Tag.Assign)
            if IL[-1] == 'LC' or IL[-1] == 'LI':
                IL[-1] = 'PUSH'
            else:
                raise SyntaxException('bad lvalue in assignment')
            expression(Tag.Assign)
            expr_type = tmp
            IL.append('SC' if expr_type == Type.CHAR else 'SI')
        elif token == Tag.Cond:
            match(Cond)
            IL.append('JZ')
            IL.append(None)
            addr = len(IL) - 1  # get the last address
            expression(Tag.Assign)
            if token == ':':
                match(':')
            else:
                raise Exception
                sys.exit()
            IL[addr] = len(IL) - 1 + 3
            IL.append('JMP')
            IL.append(None)
            addr = len(IL) - 1
            expression(Tag.Cond)
            IL[addr] = len(IL)
        elif token == Tag.Lor:
            match(Tag.Lor)
            IL.append('JNZ')
            IL.append(None)
            addr = len(IL) - 1
            expression(Tag.Lan)
            IL[addr] = len()






# get the next token
def next():
    global ptr
    global line
    global env_tree
    global token
    global token_val
    global string

    while ptr <= length:
        token = buffer[ptr]
        ptr += 1

        if token == '\n':
            line += 1
        elif token == '#':
            while buffer[ptr] != '\n':
                ptr += 1
        elif 'a' <= token <= 'z' or 'A' <= token <= 'Z' or token == '_':
            last_pos = ptr - 1
            while 'a' <=  buffer[ptr] <= 'z' or 'A' <= buffer[ptr] <= 'Z' or '0' <= buffer[ptr] <= '9':
                ptr += 1
            name = buffer[last_pos:ptr+1]
            if not env_tree.get(name):
                symbol = symbol_type()
                env_tree.put(name,symbol)
        elif '0' <= token <= '9':
            token_val = token - '0'
            while '0' <= buffer[ptr] <= '9':
                token_val = token_val * 10 + buffer[ptr] - '0'
                ptr += 1
        elif token == '"' or token == '\'':
            last_pos = ptr - 1
            while buffer[ptr] != token:
                ptr += 1
            ptr += 1
            string = buffer[last_pos:ptr-1]
        elif token == '/':
            if buffer[ptr] == '/':
                while buffer[ptr] != '\n':
                    ptr += 1
            else:
                token = Tag.Div
        elif token == '=':
            if buffer[ptr] == '=':
                ptr += 1
                token = Tag.Eq
            else:
                token = Tag.Assign
        elif token == '+':
            if buffer[ptr] == '+':
                ptr += 1
                token = Tag.Inc
            else:
                token = Tag.Add
        elif token == '-':
            if buffer[ptr] == '-':
                ptr += 1
                token = Tag.Dec
            else:
                token = Tag.Sub
        elif token == '!':
            if buffer[ptr] == '=':
                token = Tag.Ne
            else:
                pass
        elif token == '<':
            if buffer[ptr] == '=':
                ptr += 1
                token = Tag.Le
            elif buffer[ptr] == '<':
                ptr += 1
                token = Tag.Shl
            else:
                token = Tag.Lt
        elif token == '>':
            if buffer[ptr] == '=':
                ptr += 1
                token = Tag.Ge
            elif buffer[ptr] == '>':
                ptr += 1
                token = Tag.Shr
            else:
                token = Tag.Gt
        # Why ???
        elif token == '|':
            if buffer[ptr] == '|':
                ptr += 1
                token = Tag.Lor
            else:
                token = Tag.Or
        elif token == '&':
            if buffer[ptr] == '&':
                ptr += 1
                token = Tag.Lan
            else:
                token = Tag.And
        elif token == '^':
            token = Tag.Xor
        elif token == '%':
            token = Tag.Mod
        elif token == '*':
            token = Tag.Mul
        elif token == '[':
            token = Tag.Brak
        elif token == '?':
            token = Tag.Cond
        elif token in ('~', ';', '{', '}', '(', ')', ']', ',', ':'):
            pass
        return

# Maybe change the commadn to callable class ?

# exec the IL
def execute():
    global ax
    global pc
    global sp
    while True:
        op = IL[pc]
        pc += 1

        if op == 'IMM':
            ax = IL[pc]
            pc += 1
        elif op == 'LC':
            ax = str(memory[ax])
        elif op == 'LI':
            ax = int(memroy[ax])
        elif op == 'SC':
            memory[stack[sp]] = str(ax)
            sp += 1
            # why ?? 1234 lines
        elif op == 'SI':
            memory[stack[sp]] = int(ax)
            sp += 1
        elif op == 'PUSH':
            sp -= 1
            stack[sp] = ax
        elif op == 'JMP':
            pc = IL[pc]
        elif op == 'JZ':
            pc = pc + 1 if ax else IL[pc]
        elif op == 'JNZ':
            pc = IL[pc] if ax else pc + 1
        elif op == 'CALL':
            sp -= 1
            stack[sp] = pc + 1
            pc = IL[pc]
        elif op == 'ENT':
            sp -= 1
            stack[sp] = bp
            bp = sp
            sp = sp - IL[pc]
            pc += 1
        elif op == 'ADJ':
            sp = sp + IL[pc]
            pc += 1
        elif op == 'LEV':
            sp = bp
            bp = stack[sp]
            sp += 1
            pc = stack[sp]
            sp += 1
        elif op == 'LEA':
            ax = bp + IL[pc]
            pc += 1
        elif op == 'OR':
            ax = stack[sp] | ax
            sp += 1
        elif op == 'XOR':
            ax = stack[sp] ^ ax
            sp += 1
        elif op == 'AND':
            ax = stack[sp] & ax
            sp += 1
        elif op == 'EQ':
            ax = stack[sp] == ax
            sp += 1
        elif op == 'NE':
            ax = stack[sp] != ax
            sp += 1
        elif op == 'LT':
            ax = stack[sp] < ax
            sp += 1
        elif op == 'LE':
            ax = stack[sp] <= ax
            sp += 1
        elif op == 'GT':
            ax = stack[sp] > ax
            sp += 1
        elif op == 'GE':
            ax = stack[sp] >= ax
            sp += 1
        elif op == 'SHL':
            ax = stack[sp] << ax
            sp += 1
        elif op == 'SHR':
            ax = stack[sp] >> ax
            sp += 1
        elif op == 'ADD':
            ax = stack[sp] + ax
            sp += 1
        elif op == 'SUB':
            ax = stack[sp] - ax
            sp += 1
        elif op == 'MUL':
            ax = stack[sp] * ax
            sp += 1
        elif op == 'DIV':
            ax = stack[sp] / ax
            sp += 1
        elif op == 'MOD':
            ax = stack[sp] % ax
            sp += 1

        elif op == 'EXIT':
            print('exit({})'.format(stack[sp]))
            return stack[sp]
        else:
            print('Unknown Instruction')


# read the program text
def read(filepath):
    global buffer
    with open(filepath, 'r') as f:
        buffer = f.read()


# main function
def main(filepath):
    global buffer
    buffer = read(filepath)

if __name__ == '__main__':
    # main()
    IL = ['IMM', 100, 'PUSH', 'IMM', 20, 'DIV', 'PUSH', 'EXIT']
    pc = 0
    execute()
