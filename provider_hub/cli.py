import argparse
import importlib
import importlib.util
import sys
from pathlib import Path


def _load_test_module():
    pkg_dir = Path(__file__).resolve().parent
    repo_root = pkg_dir.parent
    test_path = repo_root / 'test' / 'test_connection.py'
    if test_path.exists():
        spec = importlib.util.spec_from_file_location('test.test_connection', str(test_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    raise ImportError('Could not find test.test_connection module')


def main():
    parser = argparse.ArgumentParser(description="Provider-Hub-PY CLI")
    # -t may be provided alone (run full tests) or with three positional args:
    #   provider model enableThinking
    # We accept 0 or 3 values after -t. Example:
    #   provider-hub-py -t              -> run all tests
    #   provider-hub-py -t doubao doubao-seed-1-6-250615 true
    parser.add_argument('-t', dest='test_connection', nargs='*', metavar='provider, model, enableThinking', help='Run connection test (optionally: provider model enableThinking)')
    args = parser.parse_args()

    tc = args.test_connection
    if tc is not None:
        try:
            test_mod = _load_test_module()
        except ImportError as e:
            print(f"Error: {e}")
            print("Make sure test_connection is available inside the package.")
            return

        test_connection_main = getattr(test_mod, 'main', None)
        test_connection_single = getattr(test_mod, 'test_specific_model', None)
        if not callable(test_connection_main):
            print('test_connection.main not found or not callable in module')
            return

        def _to_bool(val):
            if isinstance(val, bool):
                return val
            if val is None:
                return False
            s = str(val).strip().lower()
            if s in ('1', 'true', 't', 'yes', 'y'):
                return True
            if s in ('0', 'false', 'f', 'no', 'n'):
                return False
            return bool(s)

        if isinstance(tc, list) and len(tc) == 3:
            provider_arg = tc[0]
            model_arg = tc[1]
            enable_thinking_arg = _to_bool(tc[2])

            try:
                test_connection_single(provider_arg, model_arg, enable_thinking_arg)
            except Exception as e:
                print(f"Error running test_connection: {e}")
        else:
            test_connection_main()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
