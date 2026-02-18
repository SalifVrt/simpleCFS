"""Main script for simpleCFS."""

from . import cfsengine

def main():
    print("Hello from simplecfs!")

    engine = cfsengine.CFSEngine()
    engine.run()


if __name__ == "__main__":
    main()
