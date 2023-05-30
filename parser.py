from llvmlite import ir, binding
from rply import ParserGenerator
import sys
import re

#-----------------------------------------------------------------------------------------------------------------------------
func2=None
builder2=None
flag=False
typeis=None
values=[None]
ptr=[None]*100
var_num=0
value_num=[None]*100
count=[1]*100
func_return=0
new_module=None
#-----------------------------------------------------------------------------------------------------------------------------


class CodeGen():
    def __init__(self):
        self.binding = binding
        self.binding.initialize()
        self.binding.initialize_native_target()
        self.binding.initialize_native_asmprinter()
        self._config_llvm()
        self._create_execution_engine()
        self._declare_print_function()

    def _config_llvm(self):
        #Config
        global base_func
        self.module = ir.Module(name=__file__)
        self.module.triple = self.binding.get_default_triple()
        
        func_type = ir.FunctionType(ir.VoidType(), [], False)
        base_func = ir.Function(self.module, func_type, name="main")
        block = base_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)


    def _create_execution_engine(self):
        #Engine
        target = self.binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        backing_mod = binding.parse_assembly("")
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        self.engine = engine

    def _declare_print_function(self):
        #Printf
        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")
        self.printf = printf

    def _compile_ir(self):
        #Compile
        self.builder.ret_void()



        
        #OPTIMIZATOR1
        global new_module
        new_module=self.module
        for x in range(0,len(value_num)):
            if value_num[x]:
                TryVal=value_num[x]
                #Strip
                if hasNumbers(TryVal):
                    TryVal=TryVal[:-1]
                if hasNumbers(TryVal):
                    TryVal=TryVal[:-1]
                Object = re.search(r'store[^\@]*@"'+TryVal+'"', str(self.module))
                if Object:
                    print(Object.group())
                    Object = re.search(r'load[^\@]*@"'+TryVal+'"', str(self.module))
                    if Object:
                        print(Object.group())
                    else:
                        print(TryVal," Not Found!")
                        new_module=re.sub(r'store[^\@]*@"'+TryVal+'"', "", str(new_module))
                        new_module=re.sub('@"'+TryVal+'" = internal global i32 undef', "", str(new_module))
                for y in range(1,count[x]):
                    TryVal=TryVal+str(y+1)
                    Object = re.search(r'store[^\@]*@"'+TryVal+'"', str(self.module))
                    if Object:
                        print(Object.group())
                        Object = re.search(r'load[^\@]*@"'+TryVal+'"', str(self.module))
                        if Object:
                            print(Object.group())
                        else:
                            print(TryVal," Not Found!")
                            new_module=re.sub(r'store[^\@]*@"'+TryVal+'"', "", str(new_module))
                            new_module=re.sub('@"'+TryVal+'" = internal global i32 undef', "", str(new_module))
                    #Strip
                    if hasNumbers(TryVal):
                        TryVal=TryVal[:-1]
                    if hasNumbers(TryVal):
                        TryVal=TryVal[:-1]
        #OPTIMIZATOR2
        Object = re.search(r'call i32 @"function"', str(new_module))
        if not Object:
            print('Deleting function block ...')
            new_module=re.sub(r'define i32 @"function"[^\}]*}', "", str(new_module))
        
        
        print('####################################### End of oprimizator #######################################')
        print(new_module)
        print('####################################### End of compilator #######################################')
        llvm_ir = str(new_module)
        mod = self.binding.parse_assembly(llvm_ir)
        mod.verify()
        self.engine.add_module(mod)
        self.engine.finalize_object()
        self.engine.run_static_constructors()
        return mod

    def create_ir(self):
        self._compile_ir()

    def save_ir(self, filename):
        global new_module
        with open(filename, 'w') as output_file:
            output_file.write(str(new_module))


#-----------------------------------------------------------------------------------------------------------------------------


class Number():
    def __init__(self, builder,  module, value):
        self.builder = builder
        self.module = module
        self.value = value

    def eval(self):
        #CHECKTYPE
        if typeis==ir.IntType(32):
            i = ir.Constant(ir.IntType(32), int(self.value))
        else:
            i = ir.Constant(ir.FloatType(), float(self.value))
        return i


class BinaryOp():
    def __init__(self, builder,  module, left, right):
        global typeis
        self.builder = builder
        self.module = module
        self.left = left
        self.right = right
class SingleOp():
    def __init__(self, builder,  module, left):
        self.builder = builder
        self.module = module
        self.left = left       
class TripleOp():
    def __init__(self, builder,  module, boolean, left, right):
        self.builder = builder
        self.module = module
        self.boolean = boolean
        self.left = left
        self.right = right


#CHECKBLOCK
def b_func(b):
    if flag==True:
        b = builder2
    return b

        
class Sum(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        #CHECKTYPE
        if typeis==ir.IntType(32):
            i = self.builder.add(self.left.eval(), self.right.eval())
        else:
            i = self.builder.fadd(self.left.eval(), self.right.eval())
        return i


class Sub(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        #CHECKTYPE
        if typeis==ir.IntType(32):
            i = self.builder.sub(self.left.eval(), self.right.eval())
        else:
            i = self.builder.fsub(self.left.eval(), self.right.eval())
        return i

class Mul(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        #CHECKTYPE
        if typeis==ir.IntType(32):
            i = self.builder.mul(self.left.eval(), self.right.eval())
        else:
            i = self.builder.fmul(self.left.eval(), self.right.eval())
        return i

class Div(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        #CHECKTYPE
        if typeis==ir.IntType(32):
            i = self.builder.sdiv(self.left.eval(), self.right.eval())
        else:
            i = self.builder.fdiv(self.left.eval(), self.right.eval())
        return i


class Equal(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.icmp_signed('==', self.left.eval(), self.right.eval())
        return i
class Gthan(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.icmp_signed('>', self.left.eval(), self.right.eval())
        return i
class Lthan(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.icmp_signed('<', self.left.eval(), self.right.eval())
        return i
class Gequal(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.icmp_signed('>=', self.left.eval(), self.right.eval())
        return i
class Lequal(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.icmp_signed('<=', self.left.eval(), self.right.eval())
        return i
class Not_equal(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.icmp_signed('!=', self.left.eval(), self.right.eval())
        return i
class And_(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.and_(self.left.eval(), self.right.eval())
        return i
class Or_(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.or_(self.left.eval(), self.right.eval())
        return i
class Not_(SingleOp):
    def eval(self):
        self.builder = b_func(self.builder)
        i = self.builder.not_(self.left.eval())
        return i


class Store_(TripleOp):
    def eval(self):
        global ptr
        global var_num
        global values
        global value_num
        global count
        i=None
        #CHECKIFALREADYEXISTS
        superval=self.left.value
        values.append(superval)
        for x in range(0,len(values)-1):
            if values[x]==self.left.value:
                count[x]+=1
                value_num[x]=values[x]+str(count[x])
                superval=value_num[x]
                break
        #CHECKTYPE
        global typeis
        typeis=ir.IntType(32)
        for s in range(len(self.boolean)-1,-1,-1):
            if self.boolean[s].find(superval):
                if self.boolean[s].find(superval)=="integer":
                    typeis=ir.IntType(32)
                elif self.boolean[s].find(superval)=="float":
                    typeis=ir.FloatType()

        #STORE
        ptr[var_num] = ir.GlobalVariable(self.module, typeis, superval)
        ptr[var_num].linkage = 'internal'
        self.builder = b_func(self.builder)
        i = self.builder.store(self.right.eval(), ptr[var_num])
        var_num+=1
        if i==None:
            sys.stderr.write("Error storing variable: %s\n" %self.left.value)
            sys.exit(1)
        return i
    
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

class Load_(SingleOp):
    def eval(self):
        global flag
        global ptr
        global var_num
        global base_func
        global value_num
        global count
        i=None
        check=self.left.value
        #Strip
        if hasNumbers(self.left.value):
            check=self.left.value[:-1]
        if hasNumbers(check):
            check=check[:-1]
        #CHECKIFMULTIPLECOPIES
        for x in range(0,len(value_num)-1):
            if value_num[x]==check+str(count[x]):
                check=check+str(count[x])
                break
        #LOAD
        for x in range(0,var_num):
            if("@\""+check+"\"" in str(ptr[x])):
                self.builder = b_func(self.builder)
                i = self.builder.load(ptr[x])
        if i==None:
            sys.stderr.write("Error loading variable: %s\n" %self.left.value)
            sys.exit(1)
        return i


class If_(BinaryOp):
    def eval(self):
        self.builder = b_func(self.builder)
        with self.builder.if_then(self.left.eval()):
            i = self.right.eval()
        return i


                
class Ifelse_(TripleOp):
    def eval(self):
        self.builder = b_func(self.builder)
        with self.builder.if_else(self.boolean.eval()) as (then, otherwise):
            with then:
                i = self.left.eval()
            with otherwise:
                y = self.right.eval()
        return i


goto=None
class While_():
    def __init__(self, builder,  module,boolean,right):
        self.builder = builder
        self.module = module
        self.boolean=boolean
        self.right=right
    def eval(self):
        global goto
        i=None
        self.builder = b_func(self.builder)
        for x in range(5):
            with self.builder.if_then(self.boolean.eval()):
                    
                    print("&^^^^^^^^^^^^^^^^", goto)
                    #BREAK
                    if goto=="break":
                        break
                    #CONTINUE
                    elif goto=="continue":
                        continue
                    i = self.right.eval()
        return i


class Eval_(BinaryOp):
    def eval(self):
        i = self.left.eval()
        y = self.right.eval()
        return i

func_num=0
class Print():
    def __init__(self, builder,  module, printf, value):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.value = value

    def eval(self):
        value = self.value.eval()
        #Agruments
        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = "%i \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        global func_num
        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr" + str(func_num))
        func_num+=1
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        #Call
        self.builder = b_func(self.builder)
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)
        self.builder.call(self.printf, [fmt_arg, value])



class Literal_():
    def __init__(self, builder,  module, printf, value):
        self.builder = builder
        self.module = module
        self.printf = printf
        self.value = value

    def eval(self):
        #Agruments
        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = self.value.value+" \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        global func_num
        global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr" + str(func_num))
        func_num+=1
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        #Alloca
        self.builder = b_func(self.builder)
        c_fmt_alloca = self.builder.alloca(c_fmt.type)
        self.builder.store(c_fmt, c_fmt_alloca)
        #Call
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)
        #return None
        self.builder.call(self.printf, [fmt_arg, c_fmt_alloca])


class Func_():
    def __init__(self, builder,  module, func_name, param1, stmts):
        self.builder=builder
        self.module = module
        self.func_name = func_name
        self.param1 = param1
        self.stmts=stmts
    def eval(self):
        global func2
        global builder2
        global ptr
        global var_num
        global value_num
        global count
        global flag
        global func_return
        i=None
        #BUILDER
        func_type2 = ir.FunctionType(ir.IntType(32), [ir.IntType(32), ir.IntType(32)])
        func2 = ir.Function(self.module, func_type2, name="function")
        block2 = func2.append_basic_block(name="entry")
        builder2 = ir.IRBuilder(block2)
        #STOREARGUMENTS - nuzhno peredavat tolko novie agrumenty!!!
        arg1, arg2 = func2.args
        ptr[var_num] = ir.GlobalVariable(self.module, ir.IntType(32), self.param1[0].value)
        ptr[var_num].linkage = 'internal'
        builder2.store(arg1, ptr[var_num])
        var_num+=1
        ptr[var_num] = ir.GlobalVariable(self.module, ir.IntType(32), self.param1[1].value)
        ptr[var_num].linkage = 'internal'
        builder2.store(arg2, ptr[var_num])
        var_num+=1
        #TELO
        flag=True
        y = self.stmts.eval()
        flag=False
        #RETURN
        func_return=self.func_name.value
        for x in range(0,var_num):
            if("@\""+self.func_name.value+"\"" in str(ptr[x])):
                i = builder2.load(ptr[x])
        ii=builder2.ret(i)
        if ii==None:
            sys.stderr.write("Error returning in function")
            sys.exit(1)
        return ii


class Call_():
    def __init__(self, builder,  module, func_name, param):
        self.builder=builder
        self.module = module
        self.func_name = func_name
        self.param = param
    def eval(self):
        global func2
        #LOADARGUMENTS
        self.builder = b_func(self.builder)
        for x in range(0,var_num):
            if("@\""+self.param[0].value+"\"" in str(ptr[x])):
                arg1 = self.builder.load(ptr[x])
        for x in range(0,var_num):
            if("@\""+self.param[1].value+"\"" in str(ptr[x])):
                arg2 = self.builder.load(ptr[x])
        #CALL
        i = self.builder.call(func2, [arg1, arg2])
        return i
        
        
        
#-------------------------------------------------------------------------------------------


class Parser():
    def __init__(self, module, builder,  printf, struct):
        self.pg = ParserGenerator(
            ['AND', 'NOT', 'OR', 'IF', 'ELSE',
             'WHILE', 'BREAK', 'CONTINUE', 'BEGIN', 'END',
             'INTEGER', 'FLOAT', 'FUNCTION', 'VAR', 'PROGRAM',
             'PRINT', 'OPEN_PAREN', 'CLOSE_PAREN', 'SEMI_COLON',
             'COLON', 'COMMA', 'EQUAL', 'EQUALS', 'NOT_EQUAL',
             'GTHAN', 'GEQUAL', 'LTHAN', 'LEQUAL',
             'SUM', 'SUB', 'MUL', 'DIV',
             'NUMBER', 'ID', 'LITERAL'
             ],
        precedence=[
            ('left',['SUM','SUB']),
            ('left',['DIV','MUL'])
            ]
            )
        self.module = module
        self.builder = builder
        self.printf = printf
        self.struct = struct
        
    def parse(self):

        @self.pg.production('program : head globalp functions main')
        def program(p):
            return p[3]
        
        @self.pg.production('head : PROGRAM ID SEMI_COLON')
        def head(p):
            pass
        
        @self.pg.production('globalp : declrs')
        def globalp1(p):
            return p[0]
        
        @self.pg.production('globalp : declrs globalp')
        def globalp2(p):
            return p[0],p[1]

        @self.pg.production('declrs : VAR ids COLON type SEMI_COLON')
        def declrs(p):
            return p[1]

        @self.pg.production('functions : function')
        def functions2(p):
            return p[0].eval()
        
        @self.pg.production('functions : function functions')
        def functions2(p):
            return Eval_(self.builder,self.module,p[0],p[2])
        
        @self.pg.production('function : FUNCTION ID OPEN_PAREN globalp CLOSE_PAREN COLON type SEMI_COLON BEGIN stmts END')
        def function(p):
            return Func_(self.builder,self.module,p[1],p[3],p[9])
        
        @self.pg.production('ids : ID')
        def ids1(p):
            return p[0]
        
        @self.pg.production('ids : ID COMMA ids')
        def ids2(p):
            return p[0],p[2]
            
        @self.pg.production('type : INTEGER')
        @self.pg.production('type : FLOAT')
        def type(p):
            return p[0]
        
        @self.pg.production('main : BEGIN stmts END')
        def main(p):
            return p[1]

        @self.pg.production('stmts : stmt SEMI_COLON')
        def stmts1(p):
            return p[0]
        
        @self.pg.production('stmts : stmt SEMI_COLON stmts')
        def stmts2(p):
            return Eval_(self.builder,self.module,p[0],p[2])

        @self.pg.production('stmts : BREAK SEMI_COLON stmts')
        def break_(p):
            global goto
            goto="break"
            return p[2]

        @self.pg.production('stmts : CONTINUE SEMI_COLON stmts')
        def continue_(p):
            global goto
            goto="continue"
            return p[2]
        
        @self.pg.production('stmt : ID EQUALS expression')
        def equals_(p):
            return Store_(self.builder,self.module, self.struct, p[0], p[2])
        
        @self.pg.production('stmt : IF OPEN_PAREN bool CLOSE_PAREN COLON BEGIN stmts END')
        def if_stmt(p):
            return If_(self.builder,self.module, p[2], p[6])
        
        @self.pg.production('stmt : IF OPEN_PAREN bool CLOSE_PAREN COLON BEGIN stmts END ELSE BEGIN stmts END')
        def ifelse_stmt(p):
            return Ifelse_(self.builder,self.module, p[2], p[6], p[10])
        
        @self.pg.production('stmt : WHILE OPEN_PAREN bool CLOSE_PAREN COLON BEGIN stmts END')
        def for_stmt(p):
            return While_(self.builder,self.module,p[2],p[6])

        
        @self.pg.production('stmt : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print_stmt(p):
            return Print(self.builder,self.module, self.printf, p[2])

        @self.pg.production('stmt : PRINT OPEN_PAREN LITERAL CLOSE_PAREN')
        def print_literal(p):
            return Literal_(self.builder,self.module, self.printf, p[2])


        @self.pg.production('bool : expression EQUAL expression')
        @self.pg.production('bool : expression GTHAN expression')
        @self.pg.production('bool : expression LTHAN expression')
        @self.pg.production('bool : expression GEQUAL expression')
        @self.pg.production('bool : expression LEQUAL expression')
        @self.pg.production('bool : expression NOT_EQUAL expression')
        def bool_compare(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if operator.gettokentype() == 'EQUAL':
                return Equal(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'GTHAN':
                return Gthan(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'LTHAN':
                return Lthan(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'GEQUAL':
                return Gequal(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'LEQUAL':
                return Lequal(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'NOT_EQUAL':
                return Not_equal(self.builder,self.module, left, right)


            
        @self.pg.production('bool : bool AND bool')
        def and_bool(p):
            return And_(self.builder,self.module, p[0], p[2])
        @self.pg.production('bool : bool OR bool')
        def or_bool(p):
            return Or_(self.builder,self.module, p[0], p[2])
        @self.pg.production('bool : NOT bool')
        def not_bool(p):
            return Not_(self.builder,self.module, p[1])
        @self.pg.production('bool : OPEN_PAREN bool CLOSE_PAREN')
        def paren_bool(p):
            return p[1]


        @self.pg.production('expression : expression SUM expression')
        @self.pg.production('expression : expression SUB expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        def expression(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if operator.gettokentype() == 'SUM':
                return Sum(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'SUB':
                return Sub(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'MUL':
                return Mul(self.builder,self.module, left, right)
            elif operator.gettokentype() == 'DIV':
                return Div(self.builder,self.module, left, right)

        @self.pg.production('expression : NUMBER')
        def number(p):
            return Number(self.builder,self.module, p[0].value)
        @self.pg.production('expression : SUB NUMBER')
        def number(p):
            return Number(self.builder,self.module, str(0 - int(p[1].value)))
        @self.pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
        def paren_expr(p):
            return p[1]

        @self.pg.production('expression : ID')
        def id_expr(p):
            return Load_(self.builder,self.module, p[0])
        
        @self.pg.production('expression : ID OPEN_PAREN ids CLOSE_PAREN')
        def function_expr(p):
            return Call_(self.builder, self.module,p[0],p[2])

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
