import utils
from run_test import run_test


if __name__ == '__main__':
    args = utils.main_arg_parser()
    filepath = args.filepath
    result = run_test(filepath)
    from pprint import pprint
    pprint(result)
