from lexer import Lexer
from parser import Parser, CodeGen


#---------------------------------------------------------------------------------------------------------
class BST:
    def __init__(self,token,obj):
        self.left=None
        self.right=None
        self.token=token
        self.obj=obj
        
    def insert(self,token,obj):
        if self.token:
            if token<self.token:
                if self.left is None:
                    self.left=BST(token,obj)
                else:
                    self.left.insert(token,obj)
            elif token>self.token:
                if self.right is None:
                    self.right=BST(token,obj)
                else:
                    self.right.insert(token,obj)
        else:
            self.token=token

    def find(self,val):
        if val<self.token:
            if self.left is None:
                return None
            return self.left.find(val)
        elif val>self.token:
            if self.right is None:
                return None
            return self.right.find(val)
        else:
            return self.obj

    def printBST(self):
        if self.left:
            self.left.printBST()
        print(self.token,self.obj)
        if self.right:
            self.right.printBST()

#---------------------------------------------------------------------------------------------------------

fname = "program.txt"
with open(fname) as f:
    text_input = f.read()

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)
new_tokens = lexer.lex(text_input)

token_stream=[]
for t in new_tokens:
    token_stream.append(t)
    print(t)
print('####################################### End of lexer #######################################')


    
struct=[]
i=0
for j in range(len(token_stream)):
    if token_stream[j].gettokentype()=='ID':
        if token_stream[j-1].gettokentype()=='PROGRAM':
            struct.append(BST(token_stream[j].value,'__GLOBAL__'))
        if token_stream[j-1].gettokentype()=='FUNCTION':
            typeis=None
            s=j
            while(token_stream[s+1].gettokentype()!='SEMI_COLON'):
                s+=1
            s+=1
            while(token_stream[s+1].gettokentype()!='SEMI_COLON'):
                if token_stream[s+1].gettokentype()=='COLON':
                    if token_stream[s+2].gettokentype()=='INTEGER':
                        typeis='integer'
                        break
                    elif token_stream[s+2].gettokentype()=='FLOAT':
                        typeis='float'
                        break
                s+=1
            struct.append(BST(token_stream[j].value,typeis))
            i+=1
        t=j
        while(token_stream[t-1].gettokentype()!='SEMI_COLON'):
            if token_stream[t-1].gettokentype()=='VAR' or token_stream[t-1].gettokentype()=='FUNCTION':
                typeis=None
                s=j
                while(token_stream[s+1].gettokentype()!='SEMI_COLON'):
                    if token_stream[s+1].gettokentype()=='COLON':
                        if token_stream[s+2].gettokentype()=='INTEGER':
                            typeis='integer'
                            break
                        elif token_stream[s+2].gettokentype()=='FLOAT':
                            typeis='float'
                            break
                        else:
                            sys.stderr.write("Wrong type: %s\n" %token_stream[s+2].gettokentype())
                            sys.exit(1)
                        if token_stream[j+1].gettokentype()!='OPEN_PAREN' or token_stream[j].gettokentype()!='ID':#??????????????????????
                            break
                    s+=1
                struct[i].insert(token_stream[j].value,typeis)
            t-=1

for i in range(len(struct)):
    struct[i].printBST()
print('####################################### End of BST #######################################')













codegen = CodeGen()

module = codegen.module
builder = codegen.builder
printf = codegen.printf

pg = Parser(module, builder, printf, struct)
pg.parse()
parser = pg.get_parser()
parse = parser.parse(tokens)
parse.eval()

print('####################################### End of parser #######################################')
print(module)
print('####################################### End of generator #######################################')






codegen.create_ir()
codegen.save_ir("output.ll")


