import json
import os.path
from argparse import ArgumentParser


def load_settings(parser: ArgumentParser, config_path: str) -> dict:
    if os.path.isdir(config_path):
        load_me = None
        for file in os.listdir(config_path):
            if "config" not in file.lower() or not file.lower().endswith(".json"):
                continue
            if load_me is not None:
                parser.error("Multiple config guesses found in this directory!"
                             "\nPlease specify the full path to a config file, "
                             r"or only have one .*config.*\.json$ in the directory.")
            load_me = os.path.join(config_path, file)
    else:
        load_me = config_path
    with open(load_me, 'rb') as f:
        return json.load(f)


def generate_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', help='Use configuration file CONFIG',
                            type=str, default=".")


    return parser


def main():
    parser = generate_parser()
    args = parser.parse_args()
    load_settings(parser, args.config)
    if 'func' in args:
        args.func(args)

if __name__ == '__main__':
    main()
