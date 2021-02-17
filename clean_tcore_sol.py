import click
from os.path import join


@click.command()
@click.argument('solution')
def main(solution):
    ''' The result of this script is a file named 'clean_SOLUTION'
    placed into the same folder of SOLUTION'''
    input_sol_path = solution

    with open(input_sol_path, 'r') as fin:
        strips_sol = fin.read()

    splitted_sol = strips_sol.split('\n')
    new_plan_actions = [action.replace('__', ' ') for action in splitted_sol]

    lifted_sol = '\n'.join(new_plan_actions)

    path_sol = get_path(input_sol_path)
    name_sol = get_name(input_sol_path)

    lifted_path = join(path_sol, 'clean_{}'.format(name_sol))

    with open(lifted_path, 'w') as fout:
        fout.write(lifted_sol)
    print(lifted_path)


def get_name(path):
    return path.split('/')[-1]


def get_path(path):
    if len(path.split('/')) == 1:
        return ''
    return '/'.join(path.split('/')[0:-1])

if __name__ == "__main__":
    main()
