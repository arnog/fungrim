# -*- coding: utf-8 -*-

int_types = (int, type(1<<128))

katex_function = []

class Expr(object):

    def __new__(self, arg=None, symbol_name=None):
        if isinstance(arg, Expr):
            return arg
        self = object.__new__(Expr)
        self._symbol = None
        self._integer = None
        self._text = None
        self._args = None
        if symbol_name is not None:
            self._symbol = symbol_name
        elif isinstance(arg, str):
            self._text = arg
        elif isinstance(arg, int_types):
            self._integer = arg
        return self

    def is_atom(self):
        return self._args is None

    def is_symbol(self):
        return self._symbol is not None

    def is_integer(self):
        return self._integer is not None

    def is_text(self):
        return self._text is not None

    def head(self):
        return self._args[0]

    def args(self):
        return self._args[1:]

    def __call__(self, *args):
        v = Expr()
        v._args = (self,) + tuple(Expr(arg) for arg in args)
        return v

    def __pos__(self):
        return Pos(self)
    def __neg__(self):
        return Neg(self)
    def __abs__(self):
        return Abs(self)

    def __add__(self, other):
        return Add(Expr(self), Expr(other))
    def __radd__(self, other):
        return Add(Expr(other), Expr(self))

    def __sub__(self, other):
        return Sub(Expr(self), Expr(other))
    def __rsub__(self, other):
        return Sub(Expr(other), Expr(self))

    def __mul__(self, other):
        return Mul(Expr(self), Expr(other))
    def __rmul__(self, other):
        return Mul(Expr(other), Expr(self))

    def __div__(self, other):
        return Div(Expr(self), Expr(other))
    def __rdiv__(self, other):
        return Div(Expr(other), Expr(self))
    def __truediv__(self, other):
        return Div(Expr(self), Expr(other))
    def __rtruediv__(self, other):
        return Div(Expr(other), Expr(self))

    def __pow__(self, other):
        return Pow(Expr(self), Expr(other))
    def __rpow__(self, other):
        return Pow(Expr(other), Expr(self))

    def str(self, level=0, **kwargs):
        if self._symbol is not None:
            s = str(self._symbol)
        elif self._integer is not None:
            s = str(self._integer)
        elif self._text is not None:
            s = self._text.replace('"', '\\"')
            return '"' + s + '"'
        elif self._args is not None:
            fstr = self._args[0].str(level, **kwargs)
            argstrs = [arg.str(level+1, **kwargs) for arg in self._args[1:]]
            if self._args[0] is Entry:
                s = fstr + "(" + ",\n    ".join(argstrs) + ")"
            else:
                s = fstr + "(" + ", ".join(argstrs) + ")"
        else:
            raise ValueError("no content")
        return s

    def __str__(self):
        return self.str()

    def __repr__(self):
        return self.str()

    def all_symbols(self):
        if self._symbol is not None:
            return [self]
        symbols = []
        if self._args is not None:
            for arg in self._args:
                arg_symbols = arg.all_symbols()
                for s in arg_symbols:
                    if s not in symbols:
                        symbols.append(s)
        return symbols

    # needs work
    def need_parens_in_mul(self):
        if self.is_atom():
            if self.is_integer() and self._integer < 0:
                return True
            return False
        if self._args[0] in (Add, Sub, Neg, Pos):
            return True
        return False

    # needs work
    def show_exponential_as_power(self, allow_div=True):
        if self.is_atom():
            return True
        head = self._args[0]
        if head is Div:
            allow_div = False
        if head not in (Pos, Neg, Add, Sub, Mul, Div):
            return False
        for arg in self._args[1:]:
            if not arg.show_exponential_as_power(allow_div=allow_div):
                return False
        return True

    def latex(self, in_small=False):
        if self is ConstPi: return "\\pi"
        if self is ConstI: return "i"
        if self is ConstE: return "e"
        if self is ConstGamma: return "\\gamma"
        if self is RiemannZeta: return "\\zeta"
        if self is Infinity: return "\\infty"
        if self is UnsignedInfinity: return "{\\tilde \\infty}"
        if self is GammaFunction: return "\\Gamma"
        if self is DigammaFunction: return "\\psi"
        if self is DedekindEta: return "\\eta"
        if self is DedekindEtaEpsilon: return "\\varepsilon"
        if self is DedekindSum: return "s"
        if self is EulerQSeries: return "\\phi"
        if self is PartitionsP: return "p"
        if self is DivisorSigma: return "\\sigma"
        if self is HardyRamanujanA: return "A"
        if self is Sin: return "\\sin"
        if self is Sinh: return "\\sinh"
        if self is Cos: return "\\cos"
        if self is Cosh: return "\\cosh"
        if self is Exp: return "\\exp"
        if self is Log: return "\\log"
        if self is Atan: return "\\operatorname{atan}"
        if self is Acot: return "\\operatorname{acot}"
        if self is Hypergeometric2F1: return "{}_2F_1"
        if self is GCD: return "\\gcd"
        if self is Sign: return "\\operatorname{sgn}"
        if self is Arg: return "\\arg"
        if self is ZZ: return "\\mathbb{Z}"
        if self is QQ: return "\\mathbb{Q}"
        if self is RR: return "\\mathbb{R}"
        if self is CC: return "\\mathbb{C}"
        if self is HH: return "\\mathbb{H}"
        if self.is_atom():
            if self._symbol is not None:
                if self._symbol in variable_names:
                    if len(self._symbol) == 1:
                        return self._symbol
                    else:
                        return "\\" + self._symbol
                return "\\operatorname{" + self._symbol + "}"
            if self._integer is not None:
                return str(self._integer)
            if self._text is not None:
                return "\\text{``" + str(self._text) + "''}"

        head = self._args[0]
        args = self._args[1:]

        if head is Exp:
            assert len(args) == 1
            if args[0].show_exponential_as_power():
                return Pow(ConstE, args[0]).latex(in_small=in_small)

        if head is Div:
            assert len(args) == 2
            num, den = args
            if in_small:
                numstr = num.latex(in_small=True)
                denstr = den.latex(in_small=True)
                if num.need_parens_in_mul():  # fixme!
                    numstr = "\\left( %s \\right)" % numstr
                if den.need_parens_in_mul():  # fixme!
                    denstr = "\\left( %s \\right)" % denstr
                return numstr + " / " + denstr
            else:
                numstr = num.latex()
                denstr = den.latex()
                return "\\frac{" + numstr + "}{" + denstr + "}"

        argstr = [arg.latex(in_small=in_small) for arg in args]
        if head is Where:
            return argstr[0] + "\; \\text{ where } " + ",\,".join(argstr[1:])
        if head is Pos:
            assert len(args) == 1
            return "+" + argstr[0]
        if head is Neg:
            assert len(args) == 1
            return "-" + argstr[0]
        if head is Add:
            return " + ".join(argstr)
        if head is Sub:
            for i in range(1, len(args)):
                if not args[i].is_atom() and args[i]._args[0] in (Neg, Sub):
                    argstr[i] = "\\left(" + argstr[i] + "\\right)"
            return " - ".join(argstr)
        if head is Mul:
            for i in range(len(args)):
                if args[i].need_parens_in_mul():
                    argstr[i] = "\\left(" + argstr[i] + "\\right)"
            return " ".join(argstr)
        if head is Pow:
            assert len(args) == 2
            # remove frac to try to keep it on one line
            base = args[0]
            expo = args[1]
            basestr = base.latex(in_small=in_small)
            expostr = expo.latex(in_small=True)
            if base.is_symbol() or (base.is_integer() and base._integer >= 0) or (not base.is_atom() and base._args[0] in (Abs, Binomial)):
                return "{" + basestr + "}^{" + expostr + "}"
            else:
                return "{\\left(" + basestr + "\\right)}^{" + expostr + "}"
        if head in (Sum, Integral, Product):
            assert len(args) == 2
            assert args[1]._args[0] is Tuple
            _, var, low, high = args[1]._args
            var = var.latex()
            low = low.latex(in_small=True)
            high = high.latex(in_small=True)
            if head is Sum:
                return "\\sum_{%s=%s}^{%s} %s" % (var, low, high, argstr[0])
            if head is Integral:
                return "\\int_{%s}^{%s} %s \, d%s" % (low, high, argstr[0], var)
            if head is Product:
                return "\\prod_{%s=%s}^{%s} \\left( %s \\right)" % (var, low, high, argstr[0])
        if head is Limit:
            assert len(args) == 3
            formula, var, point = args
            var = var.latex()
            point = point.latex(in_small=True)
            formula = formula.latex()
            return "\\lim_{%s \\to %s} \\left[ %s \\right]" % (var, point, formula)
        if head is Derivative:
            assert len(args) == 2
            assert args[1]._args[0] is Tuple
            _, var, point, order = args[1]._args
            var = var.latex()
            point = point.latex(in_small=True)
            orderstr = order.latex()
            if order.is_integer() and order._integer == 1:
                return "\\left[ \\frac{d}{d %s}\, %s \\right]_{%s = %s}" % (var, argstr[0], var, point)
            else:
                return "\\left[ \\frac{d^{%s}}{{d %s}^{%s}} %s \\right]_{%s = %s}" % (orderstr, var, orderstr, argstr[0], var, point)
        if head is Sqrt:
            assert len(args) == 1
            return "\\sqrt{" + argstr[0] + "}"
        if head is Abs:
            assert len(args) == 1
            return "\\left|" + argstr[0] + "\\right|"
        if head is Floor:
            assert len(args) == 1
            return "\\left\\lfloor " + argstr[0] + " \\right\\rfloor"
        if head is Ceil:
            assert len(args) == 1
            return "\\left\\lceil " + argstr[0] + " \\right\\rceil"
        if head is Less:
            return " \\lt ".join(argstr)
        if head is LessEqual:
            return " \\le ".join(argstr)
        if head is Greater:
            return " \\gt ".join(argstr)
        if head is GreaterEqual:
            return " \\ge ".join(argstr)
        if head is Equal:
            return " = ".join(argstr)
        if head is Unequal:
            return " \\ne ".join(argstr)
        if head is Subset:
            return " \\subset ".join(argstr)
        if head is Tuple:
            return "\\left(" + ", ".join(argstr) + "\\right)"
        if head is Set:
            return "\\left\{" + ", ".join(argstr) + "\\right\}"
        if head is List:
            return "\\left[" + ", ".join(argstr) + "\\right]"
        if head is BernoulliB:
            assert len(args) == 1
            return "B_{" + argstr[0] + "}"
        if head is HarmonicNumber:
            assert len(args) == 1
            return "H_{" + argstr[0] + "}"
        if head is RiemannZetaZero:
            assert len(args) == 1
            return "\\rho_{" + argstr[0] + "}"
        if head is BernoulliPolynomial:
            assert len(args) == 2
            return "B_{" + argstr[0] + "}" + "\\left(" + argstr[1] + "\\right)"
        if head is LegendrePolynomial:
            assert len(args) == 2
            return "P_{" + argstr[0] + "}" + "\\left(" + argstr[1] + "\\right)"
        if head is BesselI:
            assert len(args) == 2
            n, z = args
            nstr = n.latex(in_small=True)
            zstr = z.latex(in_small)
            return "I_{" + nstr + "}" + "\\left(" + zstr + "\\right)"
        if head is Factorial:
            assert len(args) == 1
            if args[0].is_symbol():
                return argstr[0] + " !"
            else:
                return "\\left(" + argstr[0] + "\\right)!"
        if head is RisingFactorial:
            assert len(args) == 2
            return "\\left(" + argstr[0] + "\\right)_{" + argstr[1] + "}"
        if head is Binomial:
            assert len(args) == 2
            return "{" + argstr[0] + " \\choose " + argstr[1] + "}"
        if head is AsymptoticTo:
            assert len(argstr) == 4
            return "%s \\sim %s, \; %s \\to %s" % tuple(argstr)
        if head is Mod:
            return " \\bmod ".join(argstr)
        if head is Element:
            return " \\in ".join(argstr)
        if head is NotElement:
            return " \\not\\in ".join(argstr)
        if head is SetMinus:
            return " \\setminus ".join(argstr)
        if head is Union:
            return " \\cup ".join(argstr)
        if head is Intersection:
            return " \\cap ".join(argstr)
        if head is And:
            return " \\mathbin{\\operatorname{and}} ".join("\\left(%s\\right)" % s for s in argstr)
        if head is Or:
            return " \\mathbin{\\operatorname{or}} ".join("\\left(%s\\right)" % s for s in argstr)
        if head is Not:
            assert len(args) == 1
            return " \\operatorname{not} \\left(%s\\right)" % argstr[0]
        if head is Implies:
            return " \\implies ".join("\\left(%s\\right)" % s for s in argstr)
        if head is KroneckerDelta:
            assert len(args) == 2
            xstr = args[0].latex(in_small=True)
            ystr = args[1].latex(in_small=True)
            return "\delta_{(%s,%s)}" % (xstr, ystr)
        if head is ZZGreaterEqual:
            assert len(args) == 1
            # if args[0].is_integer():
            #    return "\{%s, %s, \ldots\}" % (args[0]._integer, args[0]._integer + 1)
            return "\\mathbb{Z}_{\ge %s}" % argstr[0]
        if head is ZZLessEqual:
            assert len(args) == 1
            if args[0].is_integer():
                return "\{%s, %s, \ldots\}" % (args[0]._integer, args[0]._integer - 1)
            return "\\mathbb{Z}_{\le %s}" % argstr[0]
        if head is ZZBetween:
            assert len(args) == 2
            if args[0].is_integer():
                return "\{%s, %s, \ldots %s\}" % (argstr[0], args[0]._integer + 1, argstr[1])
            else:
                return "\{%s, %s + 1, \ldots %s\}" % (argstr[0], args[0], argstr[1])
        if head is ClosedInterval:
            assert len(args) == 2
            return "\\left[%s, %s\\right]" % (args[0].latex(in_small=True), args[1].latex(in_small=True))
        if head is OpenInterval:
            assert len(args) == 2
            return "\\left(%s, %s\\right)" % (args[0].latex(in_small=True), args[1].latex(in_small=True))
        if head is ClosedOpenInterval:
            assert len(args) == 2
            return "\\left[%s, %s\\right)" % (args[0].latex(in_small=True), args[1].latex(in_small=True))
        if head is OpenClosedInterval:
            assert len(args) == 2
            return "\\left(%s, %s\\right]" % (args[0].latex(in_small=True), args[1].latex(in_small=True))
        if head is RealBall:
            assert len(args) == 2
            return "\\left[%s \\pm %s\\right]" % (args[0].latex(in_small=True), args[1].latex(in_small=True))
        if head is DomainCodomain:
            assert len(args) == 2
            #return "%s \\rightarrow %s" % (argstr[0], argstr[1])
        if head is Conjugate:
            assert len(args) == 1
            return "\\overline{%s}" % argstr[0]
        if head is SetBuilder:
            assert len(args) == 2
            return "\\left\\{ %s : %s \\right\\}" % tuple(argstr)
        if head is Cardinality:
            assert len(args) == 1
            #return "\\text{card }" + argstr[0]
            #return "\\# " + argstr[0]
            return "\\left|" + argstr[0] + "\\right|"
        if head is Decimal:
            assert len(args) == 1
            text = args[0]._text
            if "e" in text:
                mant, expo = text.split("e")
                expo = expo.lstrip("+")
                text = mant + " \\cdot 10^{" + expo + "}"
            return text
        if head is Parenthesis:
            assert len(args) == 1
            return "\\left(" + args[0].latex() + "\\right)"
        if head is Description:
            s = ""
            for arg in args:
                if arg._text is not None:
                    s += "\\text{ " + arg._text + " }"
                else:
                    s += arg.latex()
            return s
        fstr = self._args[0].latex()
        if in_small:
            spacer = ""
        else:
            spacer = "\\!"
        s = fstr + spacer + "\\left(" + ", ".join(argstr) + "\\right)"
        return s


    def html(self, display=False, avoid_latex=False):
        katex = katex_function[0]
        if self.is_atom():
            if avoid_latex and self.is_integer():
                return str(self._integer)
            return katex(self.latex(), display=display)
        if self.head() is Decimal and avoid_latex:
            text = self.args()[0]._text
            if "e" in text:
                mant, expo = text.split("e")
                expo = expo.lstrip("+")
                text = mant + " &middot; 10<sup>" + expo + "</sup>"
            return text
        if self.head() is Table:
            return self.html_Table()
        if self.head() is Formula:
            return katex(self._args[1].latex())
        if self.head() is References:
            return self.html_References()
        if self.head() is Assumptions:
            return self.html_Assumptions()
        return katex(self.latex(), display=display)

    def html_Table(self):
        rel = self.get_arg_with_head(TableRelation)
        heads = self.get_arg_with_head(TableHeadings)
        data = self.get_arg_with_head(List)
        split = self.get_arg_with_head(TableSplit).args()[0]._integer
        cols = len(heads.args())
        num = len(data.args())
        innum = num // split
        s = ""
        s += """<table align="center" style="border:0; background-color:#fff">"""
        s += """<tr style="border:0; background-color:#fff">"""
        for outer in range(split):
            s += """<td style="border:0; background-color:#fff; vertical-align:top">"""
            s += """<table style="float: left; margin-right: 1em">"""
            s += "<tr>"
            for col in heads.args():
                s += "<th>" + col.html(display=False) + "</th>"
            s += "</tr>"
            if outer == split-1:
                end = num
            else:
                end = innum*(outer+1)
            for row in data.args()[innum*outer : end]:
                s += "<tr>"
                for col in row.args():
                    s += "<td>" + col.html(display=False, avoid_latex=True) + "</td>"
                s += "</tr>"
            s += """</table>"""
            s += "</td>"
        s += "</tr></table>"
        s += Description("Table data:", rel.args()[0], " such that ", rel.args()[1]).html(display=True)
        return s

    def html_References(self):
        s = ""
        s += """<div class="entrysubhead">References:</div>"""
        s += "<ul>"
        for ref in self._args[1:]:
            s += "<li>%s</li>" % ref._text
        s += "</ul>"
        return s

    def html_Assumptions(self):
        s = ""
        s += """<div class="entrysubhead">Assumptions:</div>"""
        for arg in self.args():
            s += arg.html(display=True)
        s += "</ul>"
        return s

    def get_arg_with_head(self, head):
        for arg in self.args():
            if not arg.is_atom() and (arg.head() is head):
                return arg
        return None

    def id(self):
        id = self.get_arg_with_head(ID)
        return id._args[1]._text

    def title(self):
        title = self.get_arg_with_head(Title)
        return title._args[1]._text

    def entry_html(self, single=False, entrydir="../entry/"):
        id = self.id()
        all_tex = []
        s = ""
        s += """<div class="entry">"""
        if single:
            s += """<div>"""
        else:
            s += """<div style="float:left; margin-top:0.5em;">"""
            s += """<a href="%s%s.html" style="margin-left:3pt">%s</a><br/>""" % (entrydir, id, id)
            s += """<button style="margin-top:0.5em; margin-bottom: 0.5em;" onclick="toggleVisible('%s:info')">Details</button>""" % id
            s += """</div>"""
            s += """<div style="margin-left:50pt">"""

        args = self.args()
        args = [arg for arg in args if arg.head() not in (ID, Variables)]

        # First item is always visible
        s += args[0].html(display=True)
        s += "</div>"

        # Remaining items may be hidden beneath the fold
        if single:
            s += """<div id="%s:info" style="padding: 1em; clear:both">""" % id
        else:
            s += """<div id="%s:info" style="display:none; padding: 1em; clear:both">""" % id

        # Remaining items
        for arg in args[1:]:
            s += arg.html(display=True)
            s += "\n\n"

        # Generate TeX listing
        for arg in self.args():
            if arg.head() in (Formula, Assumptions):
                all_tex.append(arg.args()[0].latex())

        s += """<div class="entrysubhead">TeX:</div>"""
        s += "<pre>"
        s += "\n\n".join(all_tex)
        s += "</pre>"

        # Generate symbol table
        symbols = self.all_symbols()
        s += """<div class="entrysubhead">Definitions:</div>"""
        s += Expr.definitions_table_html(symbols, center=True)

        s += """<div class="entrysubhead">Source code for this entry:</div>"""
        s += "<pre>"
        s += self.str()
        s += "</pre>"

        s += "</div></div>\n"

        return s

    @staticmethod
    def definitions_table_html(symbols, center=False):
        katex = katex_function[0]
        s = ""
        if center:
            s += """<table style="margin: 0 auto">"""
        else:
            s += """<table>"""
        s += """<tr><th>Fungrim symbol</th> <th>Notation</th> <th>Domain</th> <th>Codomain</th> <th>Description</th></tr>"""
        for symbol in symbols:
            if symbol in descriptions:
                example, domain, codomain, description = descriptions[symbol]
                s += """<tr><td><tt>%s</tt>""" % symbol.str()
                s += """<td>%s</td>""" % katex(example.latex(), False)
                domstr = ",\, ".join(dom.latex() for dom in domain)
                s += """<td>%s</td>""" % katex(domstr, False)
                if codomain is None:
                    s += """<td></td>"""
                else:
                    s += """<td>%s</td>""" % katex(codomain.latex(), False)
                s += """<td>%s</td></tr>""" % description
        s += """</table>"""
        return s

all_builtins = []

def inject_builtin(string):
    for sym in string.split():
        globals()[sym] = Expr(symbol_name=sym)
        all_builtins.append(sym)

variable_names = set()

def inject_vars(string):
    for sym in string.split():
        e = Expr(symbol_name=sym)
        globals()[sym] = e
        variable_names.add(sym)

inject_builtin("""
Parenthesis
Unknown Undefined
Where
Set List Tuple
SetBuilder
Union Intersection SetMinus Not And Or Equivalent Implies
Cardinality
Element NotElement Subset SubsetEqual
ZZ QQ RR CC HH
ZZGreaterEqual ZZLessEqual ZZBetween
ClosedInterval OpenInterval ClosedOpenInterval OpenClosedInterval
RealBall
Decimal
Equal Unequal Greater GreaterEqual Less LessEqual
Pos Neg Add Sub Mul Div Mod Inv Pow
Max Min Sign Abs Floor Ceil Arg Re Im Conjugate
NearestDecimal
Sum Product Limit Integral Derivative
AsymptoticTo
HolomorphicDomain Poles BranchPoints BranchCuts EssentialSingularities Zeros AnalyticContinuation
Infinity UnsignedInfinity
Sqrt NthRoot Log LogBase Exp
Sin Cos Tan Sec Cot Csc
Asin Acos Atan Asec Acot Acsc
Sinh Cosh Tanh Sech Coth Csch
Asinh Acosh Atanh Asech Acoth Acsch
Sinc LambertW
ConstPi ConstE ConstGamma ConstI
Binomial Factorial GammaFunction LogGamma DigammaFunction RisingFactorial HarmonicNumber
BernoulliB BernoulliPolynomial EulerE EulerPolynomial
RiemannZeta RiemannZetaZero
BesselJ BesselI BesselY BesselK
Hypergeometric2F1
LegendrePolynomial
DedekindEta EulerQSeries DedekindEtaEpsilon DedekindSum
GCD DivisorSigma
PartitionsP HardyRamanujanA
KroneckerDelta
""")

inject_builtin("""
Entry Formula ID Assumptions References Variables DomainCodomain
Description Table TableRelation TableHeadings TableSplit
Topic Title DefinitionsTable Section SeeTopics Entries
""")

inject_vars("""a b c d e f g h i j k l m n o p q r s t u v w x y z""")
inject_vars("""A B C D E F G H I J K L M N O P Q R S T U V W X Y Z""")
inject_vars("""alpha beta gamma delta epsilon zeta eta theta iota kappa mu nu xi pi rho sigma tau phi chi psi omega""")
inject_vars("""Alpha Beta Gamma Delta Epsilon Zeta Eta Theta Iota Kappa Mu Nu Xi Pi Rho Sigma Tau Phi Chi Psi Omega""")

described_symbols = []
descriptions = {}

def describe(symbol, example, domain, codomain, description):
    described_symbols.append(symbol)
    descriptions[symbol] = (example, domain, codomain, description)


describe(ZZ, ZZ, [], None, "Integers")
describe(QQ, QQ, [], None, "Rational numbers")
describe(RR, RR, [], None, "Real numbers")
describe(CC, CC, [], None, "Complex numbers")
describe(HH, HH, [], None, "Upper complex half-plane")
describe(ConstPi, ConstPi, [], RR, "The constant pi (3.14...)")
describe(ConstE, ConstE, [], RR, "The constant e (2.718...)")
describe(ConstGamma, ConstGamma, [], RR, "The constant gamma (0.577...)")
describe(ConstI, ConstI, [], CC, "Imaginary unit")
describe(Exp, Exp(z), [Element(z, CC)], CC, "Exponential function")
describe(Log, Log(z), [Element(z, SetMinus(CC, Set(0)))], CC, "Natural logarithm")
describe(RiemannZeta, RiemannZeta(s), [Element(s, SetMinus(CC, Set(1)))], CC, "Riemann zeta function")
describe(GammaFunction, GammaFunction(z), [Element(z, SetMinus(CC, ZZLessEqual(0)))], CC, "Gamma function")
describe(Factorial, Factorial(n), [Element(n, SetMinus(CC, ZZLessEqual(-1)))], CC, "Factorial")
describe(RisingFactorial, RisingFactorial(z, k), [Element(z, CC), Element(k, ZZGreaterEqual(0))], CC, "Rising factorial")
describe(BernoulliB, BernoulliB(n), [Element(n, ZZGreaterEqual(0))], QQ, "Bernoulli number")
describe(BernoulliPolynomial, BernoulliPolynomial(n, z), [Element(n, ZZGreaterEqual(0)), Element(z, CC)], CC, "Bernoulli polynomial")
describe(EulerQSeries, EulerQSeries(q), [Element(q, CC), Less(Abs(q), 1)], CC, "Euler's q-series")
describe(DedekindEta, DedekindEta(tau), [Element(tau, CC), Greater(Im(tau), 0)], CC, "Dedekind eta function")
describe(DedekindEtaEpsilon, DedekindEtaEpsilon(a,b,c,d), [Element(a, ZZ), Element(b, ZZ), Element(c, ZZ), Element(d, ZZ)], CC, "Root of unity in the functional equation of the Dedekind eta function")
describe(DedekindSum, DedekindSum(n,k), [Element(n, ZZ), Element(k, ZZGreaterEqual(1)), Equal(GCD(n,k), 1)], QQ, "Dedekind sum")
describe(GCD, GCD(n,k), [Element(n, ZZ), Element(k, ZZ)], ZZ, "Greatest common divisor")
describe(DivisorSigma, DivisorSigma(n), [Element(n, ZZ)], ZZ, "Sum of divisors function")
describe(PartitionsP, PartitionsP(n), [Element(n, ZZ)], ZZGreaterEqual(0), "Integer partition function")
describe(HardyRamanujanA, A(n,k), [Element(n, ZZ), Element(k, ZZ)], CC, "Exponential sum in the Hardy-Ramanujan-Rademacher formula")
describe(KroneckerDelta, KroneckerDelta(x,y), [Element(x, CC), Element(y, CC)], Set(0, 1), "Kronecker delta")
describe(RiemannZetaZero, RiemannZetaZero(n), [Element(n, SetMinus(ZZ, Set(0)))], CC, "Nontrivial zero of the Riemann zeta function")
describe(LegendrePolynomial, LegendrePolynomial(n,z), [Element(n, ZZGreaterEqual(0)), Element(z, CC)], CC, "Legendre polynomial")


all_entries = []
all_topics = []

def def_Topic(*args):
    topic = Topic(*args)
    all_topics.append(topic)

def make_entry(*args):
    entry = Entry(*args)
    all_entries.append(entry)

