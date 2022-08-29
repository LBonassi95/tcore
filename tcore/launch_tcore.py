from email.policy import default
import os
from os import path
from FDgrounder import ground
from FDgrounder import pddl
from tcore import writer
import tcore.data_structures as ds
from tcore import compilation
import click
import time


@click.command()
@click.argument('domain')
@click.argument('problem')
@click.argument('output')
@click.option('--optimized', is_flag=True, default=False)
@click.option('--simplify-goal', is_flag=True, default=False)
def main(domain, problem, output, optimized, simplify_goal):
    F, A, I, G, C = ground(domain, problem)
    F, A, I, G, C = ds.convert(F, A, I, G, C)
    if optimized:
        compilation.OPTIMIZED = True
    if simplify_goal:
        compilation.SIMPLIFY_GOAL = True
    start_time = time.time()
    print("Starting TCORE")
    F_prime, A_prime, I_prime, G_prime = compilation.compile(F, A, I, G, C)
    print("TCORE-RUNTIME {}".format(time.time() - start_time))
    output_filename = 'compiled'
    if not path.isdir(output):
        os.system('mkdir {}'.format(output))
    writer.output_compiled_problem(F_prime, A_prime, I_prime, G_prime, output, output_filename)


if __name__ == '__main__':
    main()
