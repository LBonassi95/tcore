import os
import tcore
import writer
from os import path
from downward.FDgrounder import ground
import click
import time
from downward.FDgrounder import pddl
import data_structures as ds
SEPARATOR = '__'


def atom_str(atom):
    if len(atom.args) == 0:
        return "%s" % atom.predicate
    else:
        return "%s%s%s" % (atom.predicate, SEPARATOR, SEPARATOR.join(map(str, atom.args)))


def convert_formula(formula):
    if isinstance(formula, pddl.Atom):
        return ds.Literal(atom_str(formula), False)
    elif isinstance(formula, pddl.NegatedAtom):
        return ds.Literal(atom_str(formula), True)
    elif isinstance(formula, pddl.Disjunction):
        return ds.Or([convert_formula(part) for part in formula.parts])
    elif isinstance(formula, pddl.Conjunction):
        return ds.And([convert_formula(part) for part in formula.parts])
    elif isinstance(formula, pddl.Truth):
        return ds.TRUE()
    elif isinstance(formula, pddl.Falsity):
        return ds.FALSE()


def effect_conversion(action):
    new_effects = []
    for cond, eff in action.add_effects:
        if not cond:
            new_effects.append(ds.Effect(ds.TRUE(), convert_formula(eff)))
        else:
            new_cond = [convert_formula(lit) for lit in cond]
            new_effects.append(ds.Effect(ds.And(new_cond).simplified(), convert_formula(eff)))
    for cond, eff in action.del_effects:
        eff_neg = eff.negate()
        if not cond:
            new_effects.append(ds.Effect(ds.TRUE(), convert_formula(eff_neg)))
        else:
            new_cond = [convert_formula(lit) for lit in cond]
            new_effects.append(ds.Effect(ds.And(new_cond).simplified(), convert_formula(eff_neg)))
    return new_effects


def convert_constraint(c):
    if c.kind == ds.ALWAYS:
        return ds.Always(convert_formula(c.gd1))
    elif c.kind == ds.SOMETIME:
        return ds.Sometime(convert_formula(c.gd1))
    elif c.kind == ds.ATMOSTONCE:
        return ds.AtMostOnce(convert_formula(c.gd1))
    elif c.kind == ds.SOMETIMEBEFORE:
        return ds.SometimeBefore(convert_formula(c.gd1), convert_formula(c.gd2))
    elif c.kind == ds.SOMETIMEAFTER:
        return ds.SometimeAfter(convert_formula(c.gd1), convert_formula(c.gd2))


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
        A_new.append(ds.Action(action.name.replace(' ', SEPARATOR).replace('(', '').replace(')',''), pre, effects))
    for c in C:
        C_new.append(convert_constraint(c))
    return F_new, A_new, I_new, G_new, C_new

@click.command()
@click.argument('domain')
@click.argument('problem')
@click.argument('output')
def main(domain, problem, output):
    F, A, I, G, C = ground(domain, problem)
    F, A, I, G, C = convert(F, A, I, G, C)
    start_time = time.time()
    print("Starting TCORE")
    F_prime, A_prime, I_prime, G_prime = tcore.tcore(F, A, I, G, C)
    print("TCORE-RUNTIME {}".format(time.time() - start_time))
    output_filename = 'compiled'
    if not path.isdir(output):
        os.system('mkdir {}'.format(output))
    writer.output_compiled_problem(F_prime, A_prime, I_prime, G_prime, output, output_filename)


if __name__ == '__main__':
    main()
