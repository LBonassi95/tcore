from tcore.data_structures import convert
from FDgrounder import ground
from FDgrounder import pddl
from tcore.compilation import compile
import pytest
import time
import pkg_resources

def test_tcore_installation():
    domain = pkg_resources.resource_filename(__name__, 'PDDL/domain.pddl')
    problem = pkg_resources.resource_filename(__name__, 'PDDL/p01.pddl')
    F, A, I, G, C = ground(domain, problem)
    F, A, I, G, C = convert(F, A, I, G, C)
    start_time = time.time()
    print("Starting TCORE")
    compile(F, A, I, G, C)
    print("TCORE-RUNTIME {}".format(time.time() - start_time))