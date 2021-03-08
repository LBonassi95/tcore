# TCORE

Use the script launch_tcore.py to compile a problem.

syntax: python launch_tcore.py domain_path problem_path output_path

The results of tcore are output_path/compiled_dom.pddl and output_path/compiled_prob.pddl

Before validating a solution, use clean_tcore_sol.py

syntax: python clean_tcore_sol.py solution_path

# Requirements:

The package downward from https://github.com/LBonassi95/downward is required in this directory.

The scripts where tested with a python version >= 3.6 

# Benchmarks

Experimental analisys of tcore was done on the benchmarks that can be found at https://github.com/LBonassi95/Benchmarks-ICAPS-2021
