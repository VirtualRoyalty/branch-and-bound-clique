from run_test import *


if __name__ == '__main__':
    args = utils.main_arg_parser()
    filepath = args.filepath
    result = run_test(filepath)
    from pprint import pprint
    pprint(result)
