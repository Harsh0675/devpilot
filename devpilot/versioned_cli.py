"""Version-stable entry point for DevPilot releases."""
import sys

from . import __version__
from .cli import main as cli_main


def main():
    if '--version' in sys.argv[1:]:
        print(f'DevPilot {__version__}')
        return
    cli_main()


if __name__ == '__main__':
    main()
