"""Automatisk retting av R1-02-derivasjonsregler.

Hver sjekk i SJEKKER er én deltest, og poengene fordeles likt på dem.
De samme sjekkene ligger i "Test løsningen din"-cellen nederst i notebooken.
"""
import pytest

from notebook_loader import last_notebook

def naer(a, b, rel=1e-3):
    """Sant hvis tallet a er innenfor rel (relativt) av b."""
    try:
        a, b = float(a), float(b)
    except (TypeError, ValueError):
        return False
    if b == 0:
        return abs(a) < 1e-9
    return abs(a - b) <= rel * abs(b)


def S(tekst):
    """Gjør tekst om til et sympy-uttrykk, f.eks. S("x**2 - 1")."""
    import sympy
    return sympy.sympify(tekst, locals={n: sympy.Symbol(n) for n in ("N", "O", "Q", "S")})


def lik(a, b):
    """Sant hvis a og b er matematisk like.

    Lister og mengder sammenlignes uten hensyn til rekkefølge, tupler (koordinater) i rekkefølge.
    """
    import sympy
    if a is None:
        return False
    if isinstance(b, tuple):
        if not isinstance(a, (tuple, list, sympy.Tuple)) or len(a) != len(b):
            return False
        return all(lik(x, y) for x, y in zip(a, b))
    if isinstance(b, (list, set)):
        if isinstance(a, sympy.FiniteSet):
            a = list(a)
        if not isinstance(a, (list, tuple, set)) or len(a) != len(b):
            return False
        rest = list(a)
        for y in b:
            for i, x in enumerate(rest):
                if lik(x, y):
                    del rest[i]
                    break
            else:
                return False
        return True
    if isinstance(b, dict):
        if not isinstance(a, dict) or len(a) != len(b):
            return False
        a = {str(k): v for k, v in a.items()}
        return all(str(k) in a and lik(a[str(k)], v) for k, v in b.items())
    try:
        a, b = sympy.sympify(a), sympy.sympify(b)
    except (sympy.SympifyError, TypeError):
        return False
    vanlige = lambda u: u.subs({s: sympy.Symbol(s.name) for s in u.free_symbols})
    a, b = vanlige(a), vanlige(b)
    if isinstance(a, sympy.Set) or isinstance(b, sympy.Set):
        return a == b
    if getattr(b, "is_Relational", False):
        return a == b
    try:
        return sympy.simplify(a - b) == 0
    except TypeError:
        return a == b

oppgave = last_notebook("oppgave")

SJEKKER = [
    ('1a', 'd_1a skal være den deriverte av x²·eˣ', "lik(d_1a, S('2*x*exp(x) + x**2*exp(x)'))"),
    ('1b', 'd_1b skal være den deriverte av ln(x)/x', "lik(d_1b, S('(1 - log(x))/x**2'))"),
    ('1c', 'd_1c skal være den deriverte av (3x² + 1)⁵', "lik(d_1c, S('30*x*(3*x**2 + 1)**4'))"),
    ('1d', 'd_1d skal være den deriverte av √(4x + 1)', "lik(d_1d, S('2/sqrt(4*x + 1)'))"),
    ('2_riktig', 'sjekk_derivert(x³, 3x²) skal gi True', "sjekk_derivert(S('x**3'), S('3*x**2')) == True"),
    ('2_annen_form', 'sjekk_derivert skal godta svar på en annen form', "sjekk_derivert(S('x**2*exp(x)'), S('x*exp(x)*(x + 2)')) == True"),
    ('2_feil', 'sjekk_derivert(x³, 3x) skal gi False', "sjekk_derivert(S('x**3'), S('3*x')) == False"),
    ('3', 'd_3 skal være den deriverte av ln(1 + e^(2x))', "lik(d_3, S('2*exp(2*x)/(1 + exp(2*x))'))"),
    ('4', 'tangent_4 skal være y = 2x - e', "lik(tangent_4, S('2*x - E'))"),
    ('5', 'def_exp, def_ln og def_x3 skal være eˣ, 1/x og 3x²', "lik(def_exp, S('exp(x)')) and lik(def_ln, S('1/x')) and lik(def_x3, S('3*x**2'))"),
]


@pytest.mark.parametrize(
    "beskrivelse,uttrykk", [s[1:] for s in SJEKKER], ids=[s[0] for s in SJEKKER]
)
def test_sjekk(beskrivelse, uttrykk):
    navnerom = {**vars(oppgave), "naer": naer, "lik": lik, "S": S}
    assert eval(uttrykk, navnerom), beskrivelse
