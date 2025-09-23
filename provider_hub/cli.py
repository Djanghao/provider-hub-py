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
    parser.add_argument('-t', '--test', dest='test_connection', nargs='*', metavar=('provider', 'model'), help='Run connection test (optionally: provider model)')
    parser.add_argument('-q', '--quick-test', dest='test_connection_quick', nargs='*', metavar='provider', help='Run quick connection test (optionally: provider)')
    parser.add_argument('-k', '--thinking', dest='enable_thinking', action="store_true", help='Enable thinking for certain models')
    args = parser.parse_args()

    tc = args.test_connection
    tcq = args.test_connection_quick
    if tc is not None:
        if isinstance(tc, list) and len(tc) == 2:
            provider_arg = tc[0]
            model_arg = tc[1]
            enable_thinking_arg = args.enable_thinking
            try:
                test_connection(provider_arg, model_arg, enable_thinking_arg)
            except Exception as e:
                print(f"Error running test_connection: {e}")
        elif isinstance(tc, list) and len(tc) == 0:
            test_connection()
        else:
            parser.error("When using -t provide either no args or exactly 2 args: provider model")
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
            parser.error("When using -q provide either no args or exactly 1 arg: provider")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
