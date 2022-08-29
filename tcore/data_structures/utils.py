from FDgrounder import pddl
from . import *

SEPARATOR = '__'


def atom_str(atom):
    if len(atom.args) == 0:
        return "%s" % atom.predicate
    else:
        return "%s%s%s" % (atom.predicate, SEPARATOR, SEPARATOR.join(map(str, atom.args)))


def convert_formula(formula):
    if isinstance(formula, pddl.Atom):
        return Literal(atom_str(formula), False)
    elif isinstance(formula, pddl.NegatedAtom):
        return Literal(atom_str(formula), True)
    elif isinstance(formula, pddl.Disjunction):
        return Or([convert_formula(part) for part in formula.parts])
    elif isinstance(formula, pddl.Conjunction):
        return And([convert_formula(part) for part in formula.parts])
    elif isinstance(formula, pddl.Truth):
        return TRUE()
    elif isinstance(formula, pddl.Falsity):
        return FALSE()


def effect_conversion(action):
    new_effects = []
    for cond, eff in action.add_effects:
        if not cond:
            new_effects.append(Effect(TRUE(), convert_formula(eff)))
        else:
            new_cond = [convert_formula(lit) for lit in cond]
            new_effects.append(Effect(And(new_cond).simplified(), convert_formula(eff)))
    for cond, eff in action.del_effects:
        eff_neg = eff.negate()
        if not cond:
            new_effects.append(Effect(TRUE(), convert_formula(eff_neg)))
        else:
            new_cond = [convert_formula(lit) for lit in cond]
            new_effects.append(Effect(And(new_cond).simplified(), convert_formula(eff_neg)))
    return new_effects


def convert_constraint(c):
    if c.kind == ALWAYS:
        return Always(convert_formula(c.gd1))
    elif c.kind == SOMETIME:
        return Sometime(convert_formula(c.gd1))
    elif c.kind == ATMOSTONCE:
        return AtMostOnce(convert_formula(c.gd1))
    elif c.kind == SOMETIMEBEFORE:
        return SometimeBefore(convert_formula(c.gd1), convert_formula(c.gd2))
    elif c.kind == SOMETIMEAFTER:
        return SometimeAfter(convert_formula(c.gd1), convert_formula(c.gd2))


def convert(F, A, I, G, C):
    F_new = []
    I_new = []
    A_new = []
    C_new = []
    for atom in F:
        F_new.append(convert_formula(atom))
    for atom in I:
        I_new.append(convert_formula(atom))
    G_new = convert_formula(G)
    for action in A:
        pre = [convert_formula(pre) for pre in action.precondition]
        effects = effect_conversion(action)
        A_new.append(Action(action.name.replace(' ', SEPARATOR).replace('(', '').replace(')',''), pre, effects))
    for c in C:
        C_new.append(convert_constraint(c))
    return F_new, A_new, I_new, G_new, C_new