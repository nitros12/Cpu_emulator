import copy
from formatter import format_string

import pyparsing as pp


# generates math trees, etc

# this

jumplabels = 0

class ParseException(Exception):
    pass


class languageSyntaxOBbase:
    """Base class for language objects"""
    def __init__(self):
        self.parent = None
        self.children = [None]

    def parent_own_children(self):
        """Initiates filling of child parents (for codegen callbacks)"""
        #print("{0} parenting children: {0.children}".format(self))
        self.parent_children(self.children)

    def parent_children(self, *children):
        for i in children:
            if isinstance(i, languageSyntaxOBbase):
                i.set_parent(self)
                i.parent_own_children()
            elif isinstance(i, (list, tuple, pp.ParseResults)):
                self.parent_children(*i)

    def set_parent(self, parent):
        self.parent = parent

    def get_variable(self, VarName):
        """Finds stack position of a variable, bubbles up to the parent function"""
        if not self.parent:
            raise ParseException(
                "object: {} attempted to gain variable {}, but it has no parent".
                format(self, VarName))

        else:
            # this should bubble up to the parent function
            return self.parent.get_variable(VarName)

    def assemble(self):
        return ["nop"]

    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <children: {1}>>".format(
            self, ", ".join("{}".format(str(i)) for i in self.children))



class mathOP(languageSyntaxOBbase):
    def __init__(self, *children):  # , op, b):
        super().__init__()
        self.children = children

    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <children: {1}>>".format(
            self, ", ".join("{}".format(str(i)) for i in self.children))

    def assemble(self):
        """
        Use stack, infix -> postfix ->the stack machine -> return variable in @RET
        """
        return ["nop"]  # TODO: This pls


class assignOP(languageSyntaxOBbase):
    def __init__(self, setter, val):
        super().__init__()
        self.setter = setter
        self.val = val

        self.children = [val]


    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <setter: {0.setter}> <val: {0.val}>>".format(
            self)

    def assemble(self):
        variable = self.get_variable(self.setter)
        value = self.val.assemble()

        return ["mov @ret {}".format(variable)]


class variableOB(languageSyntaxOBbase):
    def __init__(self, name, initial_val):
        super().__init__()
        self.name = name
        self.initial = initial_val

    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <name: {0.name}> <initial: {0.initial}>>".format(
            self)

    def __eq__(self, other):
        return self.name == other


class programList(languageSyntaxOBbase):
    def __init__(self, *children):
        super().__init__()
        self.children = children

    def assemble(self):
        return [i.assemble()
                for i in self.children]  # we're gonna get reallly nested


class comparisonOB(languageSyntaxOBbase):

    replaceMap = {  # inversed, skips
        "<": "meje",
        ">": "leje",
        "==": "nqje",
        "!=": "eqje",
        ">=": "lje",
        "<=": "mje"
    }

    def __init__(self, left, comp, right):
        super().__init__()
        self.comp = self.replaceMap[comp]
        self.left = left
        self.right = right

    def __str__(self):
        return "<{0.__class__.__name__}:{0.comp} <parent: {0.parent.__class__.__name__}> <lhs: {0.left}> <rhs: {0.right}>>".format(
            self)


class whileTypeOB(languageSyntaxOBbase):
    def __init__(self, comp, *codeblock):
        super().__init__()
        self.comp = comp
        self.codeblock = codeblock
        self.children = [self.codeblock, self.comp]

    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <comparison: {0.comp}> <codeblock: {1}>>".format(
            self, ", ".join("{}".format(str(i)) for i in self.codeblock))

    def assemble(self):
        jid = jumplabels
        jumplabels += 1
        comparator = "_jump_start_{} CMP {} {}".format(jid, self.get_variable(self.comp.left), self.get_variable(self.comp.right))
        jump = "{} jump_end_{}".format(self.comp.comp, jid)

        return [comparator, jump, [i.assemble() for i in self.codeblock], "jmp jump_start_{}".format(jid),  "_jump_end_{} nop".format(jid)]


class ifTypeOB(languageSyntaxOBbase):
    def __init__(self, comp, *codeblock):
        super().__init__()
        self.comp = comp
        self.codeblock = codeblock
        self.children = [self.codeblock, self.comp]

    def assemble(self):
        jid = jumplabels
        jumplabels += 1
        comparator = "CMP {} {}".format(self.get_variable(self.comp.left), self.get_variable(self.comp.right))
        jump = "{} jump_end_{}".format(self.comp.comp, jid)

        return [copmarator, jump, [i.assemble() for i in self.codeblock], "_jump_end_{} NOP".format(jid)]


    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <comparison: {0.comp}> <codeblock: {1}>>".format(
            self, ", ".join("{}".format(str(i)) for i in self.codeblock))


def languageSyntaxOB(type_, *children):
    types = {  # TODO: correct parser to do any form of "word (stuff) {code}"
        "while": whileTypeOB,
        "if": ifTypeOB
    }

    return types.get(type_)(*children)


class functionCallOB(languageSyntaxOBbase):
    def __init__(self, functionName, children):
        super().__init__()
        self.functionName = functionName
        self.children = children

    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <name: {0.functionName}> <args: {1}>>".format(
            self, ", ".join("{}".format(str(i)) for i in self.children))


class varList(languageSyntaxOBbase):
    def __init__(self, *children):
        super().__init__()
        self.children = children


class functionDefineOB(languageSyntaxOBbase):
    def __init__(self, name, params, vars_, children):
        super().__init__()
        self.name = name
        self.params = params
        self.vars_ = vars_
        self.children = children

    def __str__(self):
        return "<{0.__class__.__name__} object: <parent: {0.parent.__class__.__name__}> <name: {0.name}> <params: {0.params}> <vars: {0.vars_}> <children: {0.children}>>".format(
            self)

    def get_variable(self, VarName):
        if not self.parent:
            raise ParseException(
                "object: {} attempted to gain variable {}, but it has no parent".
                format(self, VarName))

        else:
            '''
            func wew(a,b,c){
                vars{
                    d:=0;
                    e:=4;
                }
                program{
                    return a
                }
            }


            stack; |var| position relative to @lstk, position in var/ param list:

            |a|  + 3, 0
            |b|  + 2, 1
            |c|  + 1, 2
            |old stack pointer| +- 0
            |d|  - 1, 0
            |e|  - 2, 1

            '''
            if VarName in self.params:
                return "[@lstk+{}]".format(self.params.vars_[::-1].index(
                    VarName) + 1)
            elif VarName in self.vars:
                return "[@lstk-{}]".format(self.vars_.vars_index(VarName) + 1)
            else:
                raise ParseException(
                    "Attempt to access variable not in scope. Current function: {}, variable: {}".
                    format(self.name, VarName))


class atoms:
    integer = pp.Word(pp.nums).setParseAction(lambda t: int(t[0]))
    variable = pp.Word(pp.alphas + "_", pp.alphanums + "_", exact=0)
    operand = integer | variable
    semicol = pp.Literal(";").suppress()
    equals = pp.Literal(":=").suppress()

    opening_curly_bracket = pp.Literal("{").suppress()
    closing_curly_bracket = pp.Literal("}").suppress()

    lparen = pp.Literal("(").suppress()
    rparen = pp.Literal(")").suppress()
    comma = pp.Literal(",").suppress()

    comparison = pp.oneOf("== != > < >= <=")


class FuncCallSolver:
    funcStructure = pp.Forward()
    arg = funcStructure | atoms.operand
    args = arg + pp.ZeroOrMore(atoms.comma + arg)
    args.setParseAction(lambda t: varList(*t))

    funcStructure << atoms.variable + \
        pp.Group(atoms.lparen + pp.Optional(args) + atoms.rparen)
    funcStructure.setParseAction(lambda s, l, t: functionCallOB(*t))

    FuncCall = funcStructure + atoms.semicol

    def parse(self, string):
        return self.funcStructure.parseString(string).asList()

    @property
    def in_op(self):
        """something := func()
        func(func2());"""
        return self.funcStructure

    @property
    def inline(self):
        """func();"""
        return self.FuncCall


class AssignmentSolver:
    operator = FuncCallSolver.funcStructure | atoms.oprerand

    addsub = pp.oneOf("+ -")
    muldiv = pp.oneOf("* /")

    oplist = [(muldiv, 2, pp.opAssoc.RIGHT), (addsub, 2, pp.opAssoc.RIGHT)]

    expr = pp.operatorPrecedence(
        operator,
        oplist).setParseAction(lambda s, l, t: mathOP(t.asList()))

    assign = atoms.variable + atoms.equals + expr
    assignment_call = assign + atoms.semicol
    assignment_call.setParseAction(lambda s, l, t: assignOP(*t))

    def parse(self, string):
        return self.assignment_call.parseString(string).asList()

    @property
    def parseObject(self):
        return self.assignment_call


class SyntaxBlockParser:

        program = AssignmentSolver.parseObject | FuncCallSolver.inline
        languageSyntaxObject = pp.Forward()

        Syntaxblk = pp.OneOrMore(pp.Group(languageSyntaxObject) | program)

        condition = atoms.lparen + atoms.oprerand +
            atoms.comparison + atoms.oprerand + atoms.rparen
        condition.setParseAction(lambda s, l, t: comparisonOB(*t))

        syntaxBlocks = pp.oneOf("while if")

        languageSyntaxOBject << syntaxBlocks + condition + \
            atoms.opening_curly_bracket + Syntaxblk + atoms.closing_curly_bracket
        languageSyntaxOBject.setParseAction(
            lambda s, l, t: languageSyntaxOB(*t))

    def parse(self, string):
        return self.languageSyntaxOBject.parseString(string).asList()

    @property
    def parseObject(self):
        return self.languageSyntaxOBject


class StatementsObjects(SolverBase):
    statements = (pp.Word("return").suppress() + atoms.variable).setParseAction(lambda t: returnSTMOB(*t))


class OperationsObjects(SolverBase):
    def __init__(self):
        super().__init__()
        SyntaxBlocks = SyntaxBlockParser.parseObject
        assignBlocks = AssignmentSolver.parseObject
        functionCallBlocks = FuncCallSolver.inline
        statements = StatementsObjects.statements  # consistency TODO: refactor

        self.operation = SyntaxBlocks | assignBlocks | functionCallBlocks | statements

    def parse(self, string):
        return self.operation.parseString(string).asList()

    @property
    def parseObject(self):
        return self.operation


class ProgramObjects(OperationsObjects):
    def __init__(self):
        super().__init__()

        self.program = pp.Word("program").suppress(
        ) + atoms.opening_curly_bracket + pp.OneOrMore(
            self.operation) + atoms.closing_curly_bracket
        self.program.setParseAction(lambda s, l, t: programList(*t))

    def parse(self, string):
        return self.program.parseString(string).asList()

    @property
    def parseObject(self):
        return self.program


class FunctionDefineParser(SolverBase):
    def __init__(self):
        super().__init__()
        program = ProgramObjects().parseObject

        var_assign_line = atoms.variable + atoms.equals + atoms + atoms.semicol
        var_assign_line.setParseAction(lambda s, l, t: variableOB(*t))
        var_noassign_line = atoms.variable + atoms.semicol
        var_noassign_line.setParseAction(
            lambda s, l, t: variableOB(*t, 0))  # init with 0
        varline = var_assign_line | var_noassign_line
        varsblock = pp.Word("vars").suppress(
        ) + atoms.opening_curly_bracket + pp.OneOrMore(
            varline) + atoms.closing_curly_bracket
        varsblock.setParseAction(lambda s, l, t: varList(*t))

        arg = copy.copy(atoms.variable)
        arg.setParseAction(lambda s, l, t: variableOB(*t, 0))

        args = atoms.variable + pp.ZeroOrMore(atoms.comma + atoms.variable)

        argblock = atoms.lparen + pp.Optional(args) + atoms.rparen
        argblock.setParseAction(lambda s, l, t: varList(*t))

        func_name = copy.copy(atoms.variable)
        func_name.setParseAction()

        startblock = pp.Word("func ").suppress(
        ) + atoms.variable + argblock + atoms.opening_curly_bracket

        self.function = startblock + \
            pp.Optional(varsblock, default=None) + program + atoms.closing_curly_bracket
        self.function.setParseAction(lambda s, l, t: functionDefineOB(*t))

    def parse(self, string):
        return self.function.parseString(string).asList()

    @property
    def parseObject(self):
        return self.function


class ProgramSolver:
    def __init__(self):
        self.functions = pp.OneOrMore(FunctionDefineParser().function)

    def parse(self, string):
        return self.functions.parseString(string).asList()

    @property
    def parseObject(self):
        return self.functions


if __name__ == "__main__":
    a = OperationsObjects()

    print(a.parse("wew();"))
    print(a.parse("wew(lad, ayy, lmao);"))
    print(a.parse("wew(lad);"))
    print(a.parse("wew(lad(ayy), ayy);"))
    print(a.parse("wew(lad(ayy(lmao(test))));"))
    print(a.parse("wew(lad(ayy()));"))

    print(a.parse("A := A + B - C;"))
    print(a.parse("A := func() + c * 5;"))

    print(a.parse("while(a>b){wew();lad(wew());if(a<b){dothis();}}}"))

    b = FunctionDefineParser()
    print(b.parse("func wew(a,b,c){vars{a:=2;b:=4;}program{call();}}"))

    c = ProgramSolver()
    parsed = c.parse(
        "func main(wew, lad){vars{wew;}program{while(1<2){callthis();}wew:=3;}}"
    )[0]  #Type: functionDefineOB
    parsed.parent_own_children()
    print(format_string(str(parsed)))

    second = c.parse(
        "func main(a){program{if(this==that){a:=4;call(a);}while(1<3){print(this, more, that());}}} func call(a,b,c){vars{d;e:=333;f:=3;}program{d:=a*b*c;}}")
    for i in second:
        i.parent_own_children()
        print(format_string(str(i)))
