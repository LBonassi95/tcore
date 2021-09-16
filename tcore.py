import data_structures as ds

NUM = 'num'
CONSTRAINTS = 'constraints'
HOLD = 'hold'
GOAL = 'goal'
SEEN_PHI = 'seen-phi'
SEEN_PSI = 'seen-psi'
SEPARATOR = '-'
GOAL_ACHIEVED = "goal-achieved"
OPTIMIZED = False


class ProblemUnsolvableException(Exception):
    pass


def get_all_atoms(condition):
    if isinstance(condition, ds.Literal):
        return [condition]
    elif isinstance(condition, ds.And) or isinstance(condition, ds.Or):
        atoms = []
        for component in condition.components:
            atoms += get_all_atoms(component)
        return atoms
    else:
        return []


def remove_duplicates(relevant_atoms):
    elems = []
    for elem in relevant_atoms:
        if elem not in elems:
            elems.append(elem)
    return elems


def build_relevancy_dict(C):
    relevancy_dict = {}
    for c in C:
        if ds.has2gd(c.kind):
            relevant_atoms = get_all_atoms(c.gd1) + get_all_atoms(c.gd2)
        else:
            relevant_atoms = get_all_atoms(c.gd1)
        relevant_atoms = remove_duplicates(relevant_atoms)
        for atom in relevant_atoms:
            if atom.literal not in relevancy_dict:
                relevancy_dict[atom.literal] = []
            relevancy_dict[atom.literal].append(c)
    return relevancy_dict


def get_effects(action):
    if isinstance(action, ds.Action):
        for eff in action.effects:
            yield eff.condition, eff.effect
    else:
        raise Exception('Error on gamma function')


def gamma(literal, action):
    disjunction = []
    for cond, eff in get_effects(action):
        if literal == eff:
            if cond == ds.TRUE():
                # in this case cond == TRUE(), so it is a simple effect
                return ds.TRUE()
            # cond is a list of literals
            disjunction.append(cond)
    if not disjunction:
        return ds.FALSE()
    return ds.Or(disjunction)


def gamma_substitution(literal, action):
    negated_literal = literal.negate()
    gamma1 = gamma(literal, action)
    gamma2 = gamma(negated_literal, action).negate()
    conjunction = ds.And([literal, gamma2])
    return ds.Or([gamma1, conjunction])


def regression_aux(phi, action):
    return regression(phi, action).simplified()


def regression(phi, action):
    if isinstance(phi, ds.TRUE):
        return phi
    elif isinstance(phi, ds.FALSE):
        return phi
    elif isinstance(phi, ds.Literal):
        return gamma_substitution(phi, action)
    elif isinstance(phi, ds.Or):
        return ds.Or([regression(component, action) for component in phi.components])
    else:
        # And
        return ds.And([regression(component, action) for component in phi.components])


def simple_substitution(set, phi):
    if phi == ds.TRUE():
        return ds.TRUE()
    if phi == ds.FALSE():
        return ds.FALSE()
    if isinstance(phi, ds.Literal):
        if phi in set:
            return ds.TRUE()
        phi_neg = phi.negate()
        if phi_neg in set:
            return ds.FALSE()
        else:
            # phi is not in the initial state
            if phi.negated:
                return ds.TRUE()
            else:
                return ds.FALSE()
    elif isinstance(phi, ds.Or):
        return ds.Or([simple_substitution(set, component) for component in phi.components])
    else:
        # Conjunction
        return ds.And([simple_substitution(set, component) for component in phi.components])


def true_init(state, phi):
    logical_value_in_init = simple_substitution(state, phi).simplified()
    if logical_value_in_init == ds.TRUE():
        return True
    elif logical_value_in_init == ds.FALSE():
        return False
    else:
        raise Exception("ERROR in initial state evaluation of a constraint")


def get_fresh_monitoring_atom(name, number):
    return ds.Literal('{}{}{}'.format(name, SEPARATOR, number), False)


def get_constraints_to_monitor(C):
    for constr in C:
        if constr.kind != ds.ALWAYS:
            yield constr


def evaluate_constraint(constr, initial_state):
    if constr.kind == ds.SOMETIME:
        return HOLD, true_init(initial_state, constr.gd1)
    elif constr.kind == ds.SOMETIMEAFTER:
        return HOLD, true_init(initial_state, constr.gd2) or not true_init(initial_state, constr.gd1)
    elif constr.kind == ds.SOMETIMEBEFORE:
        return SEEN_PSI, true_init(initial_state, constr.gd2)
    elif constr.kind == ds.ATMOSTONCE:
        return SEEN_PHI, true_init(initial_state, constr.gd1)
    else:
        return None, true_init(initial_state, constr.gd1)


# TODO test
def get_monitoring_atoms(C, I):
    monitoring_atoms = []
    monitoring_atoms_counter = 0
    initial_state_prime = []
    for constr in get_constraints_to_monitor(C):
        type, init_state_value = evaluate_constraint(constr, I)
        monitoring_atom = get_fresh_monitoring_atom(type, monitoring_atoms_counter)
        monitoring_atoms.append(monitoring_atom)
        constr.set_monitoring_atom_predicate(monitoring_atom.literal)
        if init_state_value:
            initial_state_prime.append(monitoring_atom)
        if constr.kind == ds.SOMETIMEBEFORE:
            if true_init(I, constr.gd1):
                raise ProblemUnsolvableException("PROBLEM NOT SOLVABLE: a sometime-before is violated in the initial state")
        monitoring_atoms_counter += 1
    for constr in C:
        if constr.kind == ds.ALWAYS:
            if not true_init(I, constr.gd1):
                raise ProblemUnsolvableException("PROBLEM NOT SOLVABLE: an always is violated in the initial state")
    return initial_state_prime, monitoring_atoms


def ITC(C):
    for constr in C:
        if constr.kind in [ds.ALWAYS, ds.SOMETIMEBEFORE, ds.ATMOSTONCE]:
            yield constr


def LTC(C):
    for constr in C:
        if constr.kind in [ds.SOMETIME, ds.SOMETIMEAFTER]:
            yield constr


def create_cond_eff(condition, eff):
    conditional_effect = (condition, eff)
    return conditional_effect


def add_cond_eff(E, cond_eff):
    cond, eff = cond_eff
    if cond.simplified() != ds.FALSE():
        E.append(ds.Effect(cond, eff))


def manage_always_compilation(phi, a):
    if OPTIMIZED:
        if not can_falsify(a, phi):
            return None, False
        R = regression_aux(phi, a).simplified()
        if R == phi:
            return None, False
        else:
            return R, True
    else:
        R = regression_aux(phi, a).simplified()
        if R == phi:
            return None, False
        else:
            return R, True


def manage_amo_compilation(phi, m_atom, a, E):
    if OPTIMIZED:
        if not can_make_true(a, phi):
            return None, False
        monitoring_atom = ds.Literal(m_atom, False)
        R = regression_aux(phi, a)
        if R == phi:
            return None, False
        else:
            rho = ds.Or([R.negate(), monitoring_atom.negate(), phi]).simplified()
            add_cond_eff(E, create_cond_eff(R, monitoring_atom))
            return rho, True
    else:
        monitoring_atom = ds.Literal(m_atom, False)
        R = regression_aux(phi, a)
        if R == phi:
            return None, False
        else:
            rho = ds.Or([R.negate(), monitoring_atom.negate(), phi]).simplified()
            add_cond_eff(E, create_cond_eff(R, monitoring_atom))
            return rho, True


def manage_sb_compilation(phi, psi, m_atom, a, E):
    if OPTIMIZED:
        monitoring_atom = ds.Literal(m_atom, False)
        added_precond = (None, False)
        if can_make_true(a, phi):
            R_phi = regression_aux(phi, a)
            rho = ds.Or([R_phi.negate(), monitoring_atom]).simplified()
            added_precond = (rho, True)
        if can_make_true(a, psi):
            R_psi = regression_aux(psi, a)
            if R_psi != psi:
                add_cond_eff(E, create_cond_eff(R_psi, monitoring_atom))
        return added_precond
    else:
        monitoring_atom = ds.Literal(m_atom, False)
        R_phi = regression_aux(phi, a)
        if R_phi == phi:
            added_precond = (None, False)
        else:
            rho = ds.Or([R_phi.negate(), monitoring_atom]).simplified()
            added_precond = (rho, True)
        R_psi = regression_aux(psi, a)
        if R_psi != psi:
            add_cond_eff(E, create_cond_eff(R_psi, monitoring_atom))
        return added_precond


def manage_sometime_compilation(phi, m_atom, a, E):
    if OPTIMIZED:
        if can_make_true(a, phi):
            monitoring_atom = ds.Literal(m_atom, False)
            R = regression_aux(phi, a)
            add_cond_eff(E, create_cond_eff(R, monitoring_atom))
    else:
        monitoring_atom = ds.Literal(m_atom, False)
        R = regression_aux(phi, a)
        if R != phi:
            add_cond_eff(E, create_cond_eff(R, monitoring_atom))


def manage_sa_compilation(phi, psi, m_atom, a, E):
    if OPTIMIZED:
        R1 = regression_aux(phi, a)
        R2 = regression_aux(psi, a)
        monitoring_atom = ds.Literal(m_atom, False)
        if can_make_true(a, phi) or can_falsify(a, psi):
            cond = ds.And([R1, R2.negate()]).simplified()
            cond_eff = create_cond_eff(cond, monitoring_atom.negate())
            add_cond_eff(E, cond_eff)
        if can_make_true(a, psi):
            add_cond_eff(E, create_cond_eff(R2, monitoring_atom))
    else:
        R1 = regression_aux(phi, a)
        R2 = regression_aux(psi, a)
        monitoring_atom = ds.Literal(m_atom, False)
        if phi != R1 or psi != R2:
            cond = ds.And([R1, R2.negate()]).simplified()
            cond_eff = create_cond_eff(cond, monitoring_atom.negate())
            add_cond_eff(E, cond_eff)
        if psi != R2:
            add_cond_eff(E, create_cond_eff(R2, monitoring_atom))


def get_all_effects(a):
    for effect in a.effects:
        yield effect.effect


def get_relevant_constraints(a, relevancy_dict):
    relevant_constrains = []
    for eff in a.effects:
        constr = relevancy_dict.get(eff.effect.literal, [])
        for c in constr:
            if c not in relevant_constrains:
                relevant_constrains.append(c)
    return relevant_constrains


def tcore(F, A, I, G, C):
    relevancy_dict = build_relevancy_dict(C)
    A_prime = []
    G_prime = []
    I_prime, F_prime = get_monitoring_atoms(C, I)
    compiled_action = 0
    for c in LTC(C):
        monitoring_atom = ds.Literal(c.monitoring_atom, False)
        G_prime.append(monitoring_atom)
    G_prime = ds.And(G_prime)
    for a in A:
        E = []
        relevant_constraints = get_relevant_constraints(a, relevancy_dict)
        if len(relevant_constraints) > 0:
            compiled_action += 1
        for c in relevant_constraints:
            if c.kind == ds.ALWAYS:
                precondition, to_add = manage_always_compilation(c.gd1, a)
            elif c.kind == ds.ATMOSTONCE:
                precondition, to_add = manage_amo_compilation(c.gd1, c.monitoring_atom, a, E)
            elif c.kind == ds.SOMETIMEBEFORE:
                precondition, to_add = manage_sb_compilation(c.gd1, c.gd2, c.monitoring_atom, a, E)
            if c.kind == ds.ALWAYS or c.kind == ds.ATMOSTONCE or c.kind == ds.SOMETIMEBEFORE:
                if to_add:
                    a.precondition.append(precondition)
            if c.kind == ds.SOMETIME:
                manage_sometime_compilation(c.gd1, c.monitoring_atom, a, E)
            elif c.kind == ds.SOMETIMEAFTER:
                manage_sa_compilation(c.gd1, c.gd2, c.monitoring_atom, a, E)
        for eff in E:
            a.effects.append(eff)
        if ds.FALSE() not in a.precondition:
            A_prime.append(a)
    G_new = ds.And([G, G_prime]).simplified()

    #print("Compiled actions: {}".format(compiled_action))
    return F + F_prime, A_prime, I + I_prime, G_new


def can_falsify(a, cond):
    effects = [effect.effect for effect in a.effects]
    atoms = get_all_atoms(cond)
    for eff in effects:
        neg = eff.negate()
        if neg in atoms:
            return True
    return False


def can_make_true(a, cond):
    effects = [effect.effect for effect in a.effects]
    atoms = get_all_atoms(cond)
    for eff in effects:
        if eff in atoms:
            return True
    return False
