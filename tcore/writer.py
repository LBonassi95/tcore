import os


def domain2str(F, A):
    header = '(define (domain {domain_name})\n{domain_body})'
    requirements = '(:requirements :adl)\n'
    predicates_str = '(:predicates \n{})\n'
    actions = ''
    predicates = ''
    for atom in F:
        predicates += '\t{}\n'.format(str(atom))
    for action in A:
        actions += '{}\n\n'.format(str(action))
    domain_body = requirements + predicates_str.format(predicates) + actions
    domain_str = header.format(domain_name='compiled-domain',
                               domain_body=domain_body)
    return domain_str


def problem2str(I, G):
    header = '(define (problem {problem_name})\n(:domain {domain_name})\n{problem_body})'
    init_facts = '(:init \n{})\n'
    goal = '(:goal {})\n'.format(str(G))
    init = ''
    for atom in I:
        init += '\t{}\n'.format(str(atom))
    problem_body = init_facts.format(init) + goal
    problem_str = header.format(problem_name='compiled-problem',
                                domain_name='compiled-domain',
                                problem_body=problem_body)
    return problem_str


def output_compiled_problem(F, A, I, G, directory, output):
    domain_str = domain2str(F, A)
    problem_str = problem2str(I, G)
    output_dom_path = os.path.join(directory, output + "_dom.pddl")
    output_prob_path = os.path.join(directory, output + "_prob.pddl")
    # if not os.path.exists(directory + "output/"):
    #     os.mkdir(directory + "output/")
    with open(output_dom_path, 'w') as out_dom:
        out_dom.write(domain_str)
    with open(output_prob_path, 'w') as out_prob:
        out_prob.write(problem_str)
    print("Compiled domain:{}".format(output_dom_path))
    print("Compiled problem:{}".format(output_prob_path))