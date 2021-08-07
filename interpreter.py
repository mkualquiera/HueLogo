
class HueLogoWord:
    def __init__(self, noargs=False):
        self.noargs = noargs

    def evaluate(self,args,env):
        pass

class PrimaryWord(HueLogoWord):
    def __init__(self, handler, noargs):
        super().__init__(noargs=noargs)
        self.handler = handler
    
    def evaluate(self, args, env):
        return self.handler(args,env)

class HueLogoParser:
    def __init__(self):
        pass

    def parse(self, to_parse, env):
        word = ""
        finished_word = False
        sectioning = False
        args = ""
        depth = 0
        to_parse = to_parse.strip()

        for i, char in enumerate(to_parse):
            if not finished_word:
                if str.isspace(char):
                    if word != '':
                        finished_word = True
                        if env.is_defined(word):
                            if env.get_definition(word).noargs:
                                return word, args, to_parse[i+1:]
                        else:
                            try:
                                a = int(word)
                                return word, args, to_parse[i+1:]
                            except ValueError:
                                try:
                                    a = float(word)
                                    return word, args, to_parse[i+1:]
                                except:
                                    pass
                    continue
                if (char == '[' or char == '{') and word == '':
                    word = 'section' if char == '[' else 'softsection'
                    depth +=1 
                    sectioning = True
                    finished_word = True
                    continue
                word += char
            else:
                if char == '\n':
                    if depth <= 0:
                        return word, args, to_parse[i+1:]
                if char == '[' or char == '{':
                    depth += 1 
                if char == ']' or char == '}':
                    depth -= 1 
                    if depth == 0 and sectioning:
                        return word, args, to_parse[i+1:]
                args += char
        return word, args, ''


def sectiondef(args, env):
    env.enter_scope()
    res = env.run_string(args)
    env.leave_scope()
    return res

def softsectiondef(args,env):
    res = env.run_string(args)
    return res

def undefineddef(args, env):
    try:
        return int(args[0])
    except ValueError:
        try:
            return float(args[0])
        except:
            pass
    print(f'{args[0]} is not defined >:c')
    return False

class HueLogoInterpreter:
    def __init__(self):
        self.definitions = [{}]
        self.parser = HueLogoParser()
        self.define_primary("section",sectiondef)
        self.define_primary("softsection",softsectiondef)
        self.define_primary("undefined",undefineddef)
        self.define_primary("#enter", lambda args,env: self.enter_scope(),True)
        self.define_primary("#leave", lambda args,env: self.leave_scope(),True)

    def enter_scope(self):
        self.definitions.append({})
    
    def leave_scope(self):
        self.definitions.pop()

    def is_defined(self, word):
        for scope in reversed(self.definitions):
            if word in scope:
                return True
        return False

    def define(self, word, definition):
        self.definitions[-1][word] = definition

    def get_definition(self, word):
        for scope in reversed(self.definitions):
            if word in scope:
                return scope[word]

    def evaluate(self, word, args=None):
        #print(f'>{word}<, >>{args}<<')
        if not self.is_defined(word):
            return self.evaluate("undefined",[word, args])
        else:
            definition = self.get_definition(word)
            return definition.evaluate(args,self)

    def define_primary(self, word, handler,noargs=False):
        self.define(word,PrimaryWord(handler,noargs))
    
    def run_string(self, string):
        remainder = string
        while remainder != "":
            word, args, remainder = self.parser.parse(remainder,self)
            last = self.evaluate(word, args)
        return last
