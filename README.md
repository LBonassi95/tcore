# TCORE

Use the script launch_tcore.py to compile a problem.

syntax: python launch_tcore.py domain_path problem_path output_path

The results of tcore are output_path/compiled_dom.pddl and output_path/compiled_prob.pddl

Before validating a solution, use clean_tcore_sol.py

syntax: python clean_tcore_sol.py solution_path

# Requirements:

The package downward from https://github.com/LBonassi95/downward is required in this directory.

The scripts were tested with a Python version >= 3.6 

# Benchmarks

Benchmarks used in the ICAPS 2021 paper can be found at https://github.com/LBonassi95/Benchmarks-ICAPS-2021

# Citation

```
@inproceedings{DBLP:conf/aips/BonassiGPS21,
  author       = {Luigi Bonassi and
                  Alfonso Emilio Gerevini and
                  Francesco Percassi and
                  Enrico Scala},
  title        = {On Planning with Qualitative State-Trajectory Constraints in {PDDL3}
                  by Compiling them Away},
  booktitle    = {{ICAPS}},
  pages        = {46--50},
  publisher    = {{AAAI} Press},
  year         = {2021}
}
```
