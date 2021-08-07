import interpreter

def extract_literal(env,args):
    word = ""
    rest = ""
    for i,char in enumerate(args):
        if str.isspace(char):
            if word != "":
                rest = args[i+1:]
                break
        else:
            word += char
    return word, rest

def gather_parts(env,text):
    parts = []
    remainder = text
    while remainder != "":
        word, args, remainder = env.parser.parse(remainder,env)
        parts.append((word,args))
    return parts

def samedef(args, env):
    parts = gather_parts(env, args)
    return (env.evaluate(parts[1][0],parts[1][1]) == 
        env.evaluate(parts[0][0],parts[0][1]))

def ifdef(args, env):
    parts = gather_parts(env, args)
    if env.evaluate(*parts[0]):
        return env.evaluate(*parts[1])
    else:
        if len(parts) > 2:
            return env.evaluate(*parts[2])
    return False

class ValueDefinition(interpreter.HueLogoWord):
    def __init__(self,value):
        super().__init__(noargs=True)
        self.value = value

    def evaluate(self, args, env):
        return self.value

def setdef(args, env):
    word, rest = extract_literal(env, args)
    parts = gather_parts(env, rest)
    value = env.evaluate(*parts[0])
    env.define(word,ValueDefinition(value))
    return value

def saydef(args,env):
    parts = gather_parts(env,args)
    values = list(map(lambda x: env.evaluate(*x),parts))
    print(*values)

def quotedef(args, env):
    parts = gather_parts(env,args)
    strings = list(map(lambda x: x[1], parts))
    result = ""
    for string in strings:
        result += string
    return result

def reduce_list(operator, things):
    result = things[0]
    for thing in things[1:]:
        result = operator(result, thing)
    return result

def reductordef(args,env,operator):
    parts = gather_parts(env,args)
    values = list(map(lambda x: env.evaluate(*x),parts))
    return reduce_list(operator,values)

def monadicdef(args,env,operator):
    parts = gather_parts(env,args)
    value = env.evaluate(*parts[0])
    return operator(value)

def foralldef(args,env):
    word, rest = extract_literal(env, args)
    parts = gather_parts(env, rest)
    domain = env.evaluate(*parts[0])
    result = []
    for element in domain:
        env.enter_scope()
        env.define(word, ValueDefinition(element))
        result.append(env.evaluate(*parts[1]))
        env.leave_scope()
    return result

def listdef(args,env):
    parts = gather_parts(env,args)
    values = list(map(lambda x: env.evaluate(*x),parts))
    return values

def rangedef(args,env):
    parts = gather_parts(env,args)
    values = range(env.evaluate(*parts[0]),env.evaluate(*parts[1])+1)
    return values

def load_words(inter):
    inter.define_primary("if", ifdef)
    inter.define_primary("yes", lambda args,env: True,True)
    inter.define_primary("no", lambda args,env: False,True)
    inter.define_primary("say", saydef)
    inter.define_primary("same?", samedef)
    inter.define_primary("set", setdef)
    inter.define_primary("quote", quotedef)
    inter.define_primary("forall", foralldef)
    inter.define_primary("list", listdef)
    inter.define_primary("range", rangedef)
    inter.define_primary("sum", lambda args,env: reductordef(args,env,
        lambda a,b: a + b))
    inter.define_primary("substract", lambda args,env: reductordef(args,env,
        lambda a,b: a - b))
    inter.define_primary("multiply", lambda args,env: reductordef(args,env,
        lambda a,b: a * b))
    inter.define_primary("divide", lambda args,env: reductordef(args,env,
        lambda a,b: a / b))
    inter.define_primary("dividewhole", lambda args,env: reductordef(args,env,
        lambda a,b: a // b))
    inter.define_primary("modulo", lambda args,env: reductordef(args,env,
        lambda a,b: a % b))
    inter.define_primary("and", lambda args,env: reductordef(args,env,
        lambda a,b: a and b))
    inter.define_primary("or", lambda args,env: reductordef(args,env,
        lambda a,b: a or b))
    inter.define_primary("great?", lambda args,env: reductordef(args,env,
        lambda a,b: a > b))
    inter.define_primary("greatorsame?", lambda args,env: reductordef(args,env,
        lambda a,b: a >= b))
    inter.define_primary("less?", lambda args,env: reductordef(args,env,
        lambda a,b: a > b))
    inter.define_primary("lessorsame?", lambda args,env: reductordef(args,env,
        lambda a,b: a <= b))
    inter.define_primary("not", lambda args,env: monadicdef(args,env,
        lambda a: not a))