import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main as run_main


def main():
    run_main()


if __name__ == "__main__":
    main()
