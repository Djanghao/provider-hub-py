import argparse
import importlib
import importlib.util
import sys
from pathlib import Path
from provider_hub.test_connection import test_connection, test_connection_quick

def main():
    parser = argparse.ArgumentParser(description="Provider-Hub-PY CLI")
    # -t may be provided alone (run full tests) or with three positional args: provider, model, enableThinking
    # We accept 0 or 3 values after -t. Example:
    #   provider-hub-py -t              -> run all tests
    #   provider-hub-py -t doubao doubao-seed-1-6-250615 true
    # -qt may be provided alone (run full quick tests) or with one positional args: provider
    # We accept 0 or 1 values after -t. Example:
    #   provider-hub-py -qt              -> run all quick tests
    #   provider-hub-py -qt doubao
    parser.add_argument('-t', dest='test_connection', nargs='*', metavar='provider, model, enableThinking', help='Run connection test (optionally: provider model enableThinking)')
    parser.add_argument('-qt', dest='test_connection_quick', nargs='*', metavar='provider', help='Run quick connection test (optionally: provider)')
    args = parser.parse_args()

    tc = args.test_connection
    tcq = args.test_connection_quick
    if tc is not None:
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
                test_connection(provider_arg, model_arg, enable_thinking_arg)
            except Exception as e:
                print(f"Error running test_connection: {e}")
        elif isinstance(tc, list) and len(tc) == 0:
            test_connection()
        else:
            parser.error("When using -t provide either no args or exactly 3 args: provider model enableThinking")
    elif tcq is not None:
        if isinstance(tcq, list) and len(tcq) == 1:
            provider_arg = tcq[0]
            try:
                test_connection_quick(provider_arg)
            except Exception as e:
                print(f"Error running test_connection_quick: {e}")
        elif isinstance(tcq, list) and len(tcq) == 0:
            test_connection_quick()
        else:
            parser.error("When using -qt provide either no args or exactly 1 arg: provider")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
