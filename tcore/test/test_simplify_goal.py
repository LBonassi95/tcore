from tcore.data_structures import convert
from tcore import data_structures as ds
from FDgrounder import ground
from tcore import compilation
import pytest
import pkg_resources

def test_original_goal():
    domain = pkg_resources.resource_filename(__name__, 'PDDL/domain.pddl')
    problem = pkg_resources.resource_filename(__name__, 'PDDL/p01_disj.pddl')
    F, A, I, G, C = ground(domain, problem)
    F, A, I, G, C = convert(F, A, I, G, C)
    _, _, _, G_prime = compilation.compile(F, A, I, G, C)
    assert isinstance(G_prime.components[0], ds.Or)

def test_simplify_goal():
    domain = pkg_resources.resource_filename(__name__, 'PDDL/domain.pddl')
    problem = pkg_resources.resource_filename(__name__, 'PDDL/p01_disj.pddl')
    compilation.SIMPLIFY_GOAL = True
    F, A, I, G, C = ground(domain, problem)
    F, A, I, G, C = convert(F, A, I, G, C)
    _, _, _, G_prime = compilation.compile(F, A, I, G, C)
    assert isinstance(G_prime, ds.Literal)
