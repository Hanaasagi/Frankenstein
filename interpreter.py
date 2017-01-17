# -*-coding:UTF-8-*-

import sys
import collections
import argparse
# To prevert the conflict
if sys.version_info.major > 2:
    from builtins import id as object_id
else:
    from __builtin__ import id as object_id

# VM setting
STACK_MAX_SIZE = 128
MEMORY_MAX_SIZE = 1024
DATA_MAX_SIZE = 128

# VM composition

'''
+------------------+
|   stack    |     |  high address
|   ...      v     |
|                  |
|                  |
|                  |
|                  |
|   ...      ^     |
|   heap     |     |
+------------------+
| bss segment      |
+------------------+
| data segment     |
+------------------+
| text segment     |  low address
+------------------+
'''

stack = [None] * STACK_MAX_SIZE  # stack
data = [None] * DATA_MAX_SIZE # data segment
memory = [None] * MEMORY_MAX_SIZE  # memory (remaining memory)
pc = 0  # program counter
sp = STACK_MAX_SIZE - 1  # stack pointer
bp = 0  # stack base pointer
ax = None  # register
index_of_bp = sp


# VM supported inareuctions
instruction = ['LEA', 'IMM', 'JMP', 'CALL', 'JZ', 'JNZ', 'ENT', 'ADJ', 'LI',
    'LC', 'SI', 'SC', 'PUSH', 'OR', 'XOR', 'AND', 'EQ', 'NE', 'LT', 'GT','LE',
    'GE', 'SHL', 'SHR', 'ADD', 'SUB','MUL', 'DIV','MOD', 'OPEN', 'READ','CLOS',
    'PRTF', 'MALC', 'MSET', 'MCMP', 'EXIT']

# lexer and parser
# IL_MAX_SIZE = 512  # Intermediate language
# IL = [None] * IL_MAX_SIZE
# IL_ptr = 0  # IL pointer
IL = []  # Intermediate language
peek = None
token = None  # token in lexer
token_val = None  # token value
current_id = None  # current identifier
string = ''  # parse string
ptr = 0  # pointer which is pointing in program text
line = 0  # source line
buffer = None  # store the program text
length = 0  # length of buffer

# token's tag
class Tag(object):
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
    Lor = 144  # logical or
    Lan = 145  # logical and
    Or = 146   # bit or
    Xor = 147
    And = 148  # bit and
    Eq = 149   # ==
    Ne = 150   # !=
    Lt = 151   # <
    Gt = 152   # >
    Le = 153   # <=
    Ge = 154   # >=
    Shl = 155  # <<
    Shr = 156  # >>
    Add = 157
    Sub = 159
    Mul = 160
    Div = 161
    Mod = 162
    Inc = 163
    Dec = 164
    Brak = 165  # [

# symbol
class Symbol(object):

    def __init__(self, token, name, klass, type, value):
        self.token = token
        self.name = name
        self.klass = klass
        self.type = type
        self.value = value


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
                return env.table[name]
            env = env.pre
        return None

env_tree = Env()

# C Data Type
class Type(object):
    CHAR = 0
    INT = 1
    DOUBLE = 2
    PTR = 3

expr_type = None

# C Keywords
keywords = {
    'char': Tag.Char,
    'else': Tag.Else,
    'enum': Tag.Enum,
    'if': Tag.If,
    'int': Tag.Int,
    'return': Tag.Return,
    'sizeof': Tag.Sizeof,
    'while': Tag.While}

builtin_instruction = {
    'open':'OPEN',
    'read':'READ',
    'close':'CLOS',
    'printf':'PRTF',
    'malloc':'MALC',
    'memset':'MSET',
    'memcmp':'MCMP',
    'exit':'EXIT'}
'void', 'main'

# init
def init_env():
    global env_tree
    top_env = Env()
    # put keywords to top env
    for keyword,token in keywords.items():
        # ['token', 'name', 'klass', 'type', 'value']
        top_env.put(keyword, Symbol(
            token=token,
            name=keyword,
            klass=None,
            type=None,
            value=None)
        )
    # put instructions to top env
    for instruction,value in builtin_instruction.items():
        top_env.put(instruction, Symbol(
            token=None,
            name=instruction,
            klass=Tag.Sys,
            type=Type.INT,
            value=value)
        )
    env_tree.pre = top_env

# Syntax Exception
class SyntaxException(Exception):

    def __init__(self, msg='invalid syntax'):
        self.msg = msg

    def __str__(self):
        return 'SyntaxError: {0}'.format(self.msg)

class  RuntimeException(Exception):

    def __init__(self, msg=''):
        self.msg = msg

    def __str__(self):
        return 'RuntimeError: {0}'.format(self.msg)


# match the token and get next token
def match(tk):
    if token == tk:
        next()
    else:
        raise SyntaxException('mismatch')

def expression(level):
    print 'token in expression is ', token
    print 'level in expression is ', level
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
        print '242 line exec!!!!'
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
            expr_type = expr_type + Type.PTR

        match(')')

        IL.append('IMM')
        # CHAR 1 byte
        # INT 4 byte
        IL.append(1 if expr_type == Type.CHAR else 4)
        expr_type = Type.INT
    elif token == Tag.Id:
        match(Tag.Id)
        id = current_id

        if token == '(':
            # function call
            match('(')
            tmp = 0
            # parse the arguments
            while token != ')':
                expression(Tag.Assign)
                IL.append('PUSH')
                tmp += 1
                if token == ',':
                    match(',')
            match(')')

            if id.klass == Tag.Sys:
                IL.append(id.value)
            elif id.klass == Tag.Fun:
                IL.append('CALL')
                IL.append(id.value)
            else:
                raise SyntaxException('illegal function')
                sys.exit()

            # important !!!
            if tmp > 0:
                IL.append('ADJ')
                IL.append(tmp)
            expr_type = id.Type
        else:
            # variable
            if id.klass == Tag.Loc:
                IL.append('LEA')
                IL.append(index_of_bp - id.value)
            elif id.klass == Tag.Glo:
                IL.append('IMM')
                IL.append(id.value)
            else:
                raise Exception
                sys.exit()
            expr_type = id.type
            IL.append('LC' if id.type == Type.CHAR else 'LI')

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
            expr_type = tmp
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
        else:
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
                sys.exit()
            expression(Tag.Assign)
            expr_type = tmp
            IL.append('SC' if expr_type == Type.CHAR else 'SI')
        elif token == Tag.Cond:
            match(Tag.Cond)
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
            IL[addr] = len(IL)
            expr_type = Type.INT
        elif token == Tag.Lan:
            match(Tag.Lan)
            IL.append('JZ')
            IL.append(None)
            addr = len(IL) - 1
            expression(Tag.Or)
            IL[addr] = len(IL)
            expr_type = Type.INT
        elif token == Tag.Or:
            match(Tag.Or)
            IL.append('PUSH')
            expression(Tag.Xor)
            IL.append('OR')
            expr_type = Type.INT
        elif token == Tag.Xor:
            match(Tag.Xor)
            IL.append('PUSH')
            expression(Tag.And)
            IL.append('XOR')
            expr_type = Type.INT
        elif token == Tag.And:
            match(Tag.And)
            IL.append('PUSH')
            expression(Tag.Eq)
            IL.append('AND')
            expr_type = Type.INT
        elif token == Tag.Eq:
            match(Tag.Eq)
            IL.append('PUSH')
            expression(Tag.Ne)
            IL.append('EQ')
            expr_type = Type.INT
        elif token == Tag.Ne:
            match(Tag.Ne)
            IL.append('PUSH')
            expression(Tag.Lt)
            IL.append('NE')
            expr_type = INT
        elif token == Tag.Lt:
            match(Tag.Lt)
            IL.append('PUSH')
            expression(Tag.Shl)
            IL.append('LT')
            expr_type = INT
        elif token == Tag.Gt:
            match(Tag.Gt)
            IL.append('PUSH')
            expression(Tag.Shl)
            IL.append('GT')
            expr_type = Type.INT
        elif token == Tag.Le:
            match(Tag.Le)
            IL.append('PUSH')
            expression(Tag.Shl)
            Il.append('LE')
            expr_type = Type.INT
        elif token == Tag.Ge:
            match(Tag.Ge)
            IL.append('PUSH')
            expression(Tag.Shl)
            IL.append('GE')
            expr_type = Type.INT
        elif token == Tag.Shl:
            match(Tag.Shl)
            IL.append('PUSH')
            expression(Tag.ADD)
            IL.append('SHL')
            expr_type = Type.INT
        elif token == Tag.Shr:
            match(Tag.Shr)
            IL.append('PUSH')
            expression(Tag.Add)
            IL.append('SHR')
            expr_type = Type.INT
        elif token == Tag.Add:
            match(Tag.Add)
            IL.append('PUSH')
            expression(Tag.Mul)
            expr_type = tmp
            if expr_type > Type.PTR:
                IL.append('PUSH')
                IL.append('IMM')
                # need to support Char *
                IL.append(4)
                IL.append('MUL')
            IL.append('ADD')
        elif token == Tag.Sub:
            match(Tag.Sub)
            IL.append('PUSH')
            expression(Tag.Mul)
            if tmp > Type.PTR and tmp == expr_type:
                IL.append('SUB')
                IL.append('PUSH')
                IL.append('IMM')
                IL.append(4)
                IL.append('DIV')
                expr_type = Type.INT
            elif tmp > Type.PTR:
                IL.append('PUSH')
                IL.append('IMM')
                IL.append(4)
                IL.append('MUL')
                IL.append('SUB')
                expr_type = tmp
            else:
                IL.append('SUB')
                expr_type = tmp
        elif token == Tag.Mul:
            match(Tag.Mul)
            IL.append('PUSH')
            expression(Tag.Inc)
            IL.append('MUL')
            expr_type = tmp
        elif token == Tag.Div:
            match(Tag.Div)
            IL.append('PUSH')
            expression(Tag.Inc)
            IL.append('DIV')
            expre_type = tmp
        elif token == Tag.Mod:
            match(Tag.Mod)
            IL.append('PUSH')
            expression(Tag.Inc)
            IL.append('MOD')
            expr_type = tmp
        elif token == Tag.Inc or token == Tag.Dec:
            if IL[-1] == 'LI':
                IL[-1] = 'PUSH'
                IL.append('LI')
            elif IL[-1] == 'LC':
                IL[-1] = 'PUSH'
                IL.append('LC')
            else:
                raise Exception
                sys.exit()
            IL.append('PUSH')
            IL.append('IMM')
            IL.append(4 if expr_type > Type.PTR else 1)
            IL.append('ADD' if token == Tag.Inc else 'SUB')
            IL.append('SC' if expr_type == Type.CHAR else 'SI')
            IL.append('PUSH')
            IL.append('IMM')
            IL.append(4 if expr_type > Type.PTR else 1)
            IL.append('SUB' if token == Tag.Inc else 'ADD')
            match(token)
        elif token == Tag.Brak:
            match(Tag.Brak)
            IL.append('PUSH')
            expression(Tag.Assign)
            match(']')

            if tmp > Type.PTR:
                IL.append('PUSH')
                IL.append('IMM')
                IL.append(4)
                IL.append('Mul')
            elif tmp < Type.PTR:
                raise Exception
                sys.exit()
            expr_type = tmp - Type.PTR
            IL.append('ADD')
            IL.append('LC' if expr_type == Type.CHAR else 'LI')
        else:
            raise Exception
            sys.exit()


# parse the statement
def statement():
    addr1 = None
    addr2 = None
    if token == Tag.If:
        match(Tag.If)
        match('(')
        expression(Tag.Assign)
        match(')')

        IL.append('JZ')
        IL.append(None)
        addr2 = len(IL) - 1
        statement()

        if token == Tag.Else:
            match(Tag.Else)

            IL[addr2] = len(IL) + 2
            IL.append('JMP')
            IL.append(None)
            addr2 = len(IL) - 1

            statement()
        IL[addr2] = len(IL)
    elif token == Tag.While:
        match(Tag.While)
        addr1 = len(IL)
        match('(')
        expression(Tag.Assign)
        match(')')
        IL.append('JZ')
        IL.append(None)
        addr2 = len(IL) - 1
        statement()
        IL.append('JMP')
        IL.append(addr1)
        IL[addr2] = len(IL)
    elif token == '{':
        match('{')
        while token != '}':
            statement()
        match('}')
    elif token == Tag.Return:
        match(Tag.Return)
        if token != ';':
            expression(Tag.Assign)
        match(';')
        IL.append('LEV')
    elif token == ';':
        match(';')
    else:
        expression(Tag.Assign)
        match(';')




# Maybe it should be a generator
# get the next token
def next():
    global ptr
    global line
    global env_tree
    global peek
    global token
    global token_val
    global data
    global string
    global current_id

    while ptr < length:
        peek = buffer[ptr]
        ptr += 1

        if peek == '\n':
            line += 1
        elif peek == '#':
            # not support macro, skip  it
            while buffer[ptr] != '\n':
                ptr += 1
        elif 'a' <= peek <= 'z' or 'A' <= peek <= 'Z' or peek == '_':
            # parse identifier
            last_pos = ptr - 1
            while 'a' <=  buffer[ptr] <= 'z' or 'A' <= buffer[ptr] <= 'Z' \
                or '0' <= buffer[ptr] <= '9' or buffer == '_':
                ptr += 1
            name = buffer[last_pos:ptr]
            print name
            # look for the current env
            symbol = env_tree.get(name)
            # create new
            if symbol is None:
                # here ????
                symbol = Symbol(
                    token=Tag.Id,
                    name=name,
                    klass=None,
                    type=None,
                    value=None)
                env_tree.put(name, symbol)
                token = symbol.token
            else:
                token = symbol.token
            current_id = symbol
            return
        elif '0' <= peek <= '9':
            # parse number only Decimal, not support Hex yet
            token_val = ord(peek) - ord('0')
            while '0' <= buffer[ptr] <= '9':
                token_val = token_val * 10 + ord(buffer[ptr]) - ord('0')
                ptr += 1
            token = Tag.Num
            return
        elif peek == '"' or peek == '\'':
            # parse string, not support escape character
            last_pos = ptr
            while buffer[ptr] != peek:
                ptr += 1
            ptr += 1
            string = buffer[last_pos:ptr-1]

            # add string to data segment
            data.append(string)
            if peek == '\'':
                # single character
                token = Tag.Num
            token_val = len(data) - 1  
            return
        elif peek == '/':
            # parse the comment // or Div /
            if buffer[ptr] == '/':
                while buffer[ptr] != '\n':
                    ptr += 1
            else:
                token = Tag.Div
            return
        elif peek == '=':
            # parse == or =
            if buffer[ptr] == '=':
                ptr += 1
                token = Tag.Eq
            else:
                token = Tag.Assign
            return
        elif peek == '+':
            # parse ++ or +
            if buffer[ptr] == '+':
                ptr += 1
                token = Tag.Inc
            else:
                token = Tag.Add
            return
        elif peek == '-':
            # parse -- or -
            if buffer[ptr] == '-':
                ptr += 1
                token = Tag.Dec
            else:
                token = Tag.Sub
            return
        elif peek == '!':
            # parse !=
            if buffer[ptr] == '=':
                token = Tag.Ne
            return
        elif peek == '<':
            # parse <= or << or <
            if buffer[ptr] == '=':
                ptr += 1
                token = Tag.Le
            elif buffer[ptr] == '<':
                ptr += 1
                token = Tag.Shl
            else:
                token = Tag.Lt
            return
        elif peek == '>':
            # parse >= or >> or >
            if buffer[ptr] == '=':
                ptr += 1
                token = Tag.Ge
            elif buffer[ptr] == '>':
                ptr += 1
                token = Tag.Shr
            else:
                token = Tag.Gt
            return
        elif peek == '|':
            # parse || or |
            if buffer[ptr] == '|':
                ptr += 1
                token = Tag.Lor
            else:
                token = Tag.Or
            return
        elif peek == '&':
            # parse && or &
            if buffer[ptr] == '&':
                ptr += 1
                token = Tag.Lan
            else:
                token = Tag.And
            return
        elif peek == '^':
            # parse ^
            token = Tag.Xor
            return
        elif peek == '%':
            # parse %
            token = Tag.Mod
            return
        elif peek == '*':
            # parse * (mul or pointer)
            token = Tag.Mul
            return
        elif peek == '[':
            # parse [
            token = Tag.Brak
            return
        elif peek == '?':
            # parse  condition ? a : b
            token = Tag.Cond
            return
        elif peek in ('~', ';', '{', '}', '(', ')', ']', ',', ':'):
            # parse other character and return it as token
            token = peek
            return
        # skip other character included space tab ...


def function_parameter():
    # parse function parameter, eg (int arg1, char arg2, int *arg3)
    global index_of_bp
    params = 0
    while token != ')':
        # 
        if token == Tag.Int:
            type = Type.INT
            match(Tag.Int)
        elif token == Tag.Char:
            type = Type.CHAR
            match(Tag.Char)

        # pointer type
        while token == Tag.Mul:
            match(Tag.Mul)
            type = type + Type.PTR

        if token != Tag.Id:
            raise SyntaxException('illegal parameter declaration')
            sys.exit()

        match(Tag.Id)

        # important !!
        current_id.klass = Tag.LOC
        current_id.type = type
        current_id.value = params
        params += 1


        if token == ',':
            match(',')
        # here !!
    index_of_bp = params + 1


def function_body():
    pos_local = index_of_bp

    while token == Tag.Int or token == Tag.Char:
        if token == Tag.Int:
            base_type = Type.INT
        if token == Tag.Char:
            base_type = Type.Char
        match(token)

        while token != ';':
            type = base_type
            while token == Tag.Mul:
                match(Tag.Mul)
                type = type + Type.PTRs

            if token != Tag.Id:
                raise SyntaxException('illegal decalaration')

            match(Tag.Id)
            current_id.klass = Tag.Loc
            current_id.type = type
            pos_local += 1
            current_id.value = pos_local 
            if token == ',':
                match(',')

        match(';')
    IL.append('ENT')
    IL.append(pos_local - index_of_bp)

    while token != '}':
        statement()

    IL.append('LEV')





def function_declaration():
    match('(')
    function_parameter()
    match(')')
    match('{')
    function_body()

    # pass



def global_declaration():
    global data
    global current_id
    type = None
    i = None

    
    # parse declaration type, eg int char double
    if token == Tag.Int:
        match(Tag.Int)
        base_type = Type.INT
    elif token == Tag.Char:
        match(Tag.Char)
        base_type = Type.CHAR
    else:
        base_type = Type.INT
    # need to support double type !!!

    while token != ';' and token != '}':
        type = base_type
        # pointer type Maybe there are many *
        while token == Tag.Mul:
            match(Tag.Mul)
            type = type + Type.PTR

        if token != Tag.Id:
            raise SyntaxException('invalid declaration')
            sys.exit()

        # How to avoid duplicate declaration like this ??
        if current_id.klass is not None:
            raise SyntaxException('duplicate declaration')
            sys.exit()
        match(Tag.Id)
        current_id.type = type
        
        if token == '(':
            # It is a function
            current_id.klass = Tag.Fun
            current_id.value = len(IL)  # store the address of function
            # parse function
            function_declaration()
        else:
            # It is a variable
            current_id.klass = Tag.Glo
            current_id.value = len(data) - 1
            data.append(None)

        if token == ',':
            match(',')
    next()






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
            ax = int(memory[ax])
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
def read(file_path):
    global buffer
    global length
    with open(file_path, 'r') as f:
        buffer = f.read()
    length = len(buffer)

# parse the command
def cmd_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str, nargs=1,
                        help='specify your C file path')
    parser.add_argument('--debug', dest='debug', action='store_true',
                        help='debug mode: echo the Intermediate language')
    args = parser.parse_args()
    return args.file_path, args.debug


def test():
    global buffer
    global length
    buffer = '''
#include <stdio.h>
int x;
x = 1;
int main() {
    int i;
    i = 0;
    printf("Hello World! And i is %d\n", i);
    return 0;
}
'''
    length = len(buffer)

if __name__ == '__main__':
    file_path, debug = cmd_parser()
    init_env()
    test()
    # buffer = read(file_path)


    next()
    while token > 0:
        global_declaration()

    # init stack
    stack[sp] = 'EXIT'
    sp -= 1
    stack[sp] = 'PUSH'
    sp -= 1

    if debug:
        print('{}\nThe following is the Intermediate language\n{}'.format(buffer,IL))
        for instruction in IL:
            print instruction
    # execute()
