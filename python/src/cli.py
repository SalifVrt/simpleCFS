import os
import subprocess
import sys


def run_tests():
    """Run pytest via uv"""
    print("Starting tests...")
    result = subprocess.run(["pytest"])
    
    sys.exit(result.returncode)
    

def run_simulation(file_path="../tests/testfiles/td1.txt"):
    """Run main simulation"""
    print("Starting CFS...")
    from main import main as cfs_main
    subprocess.run([sys.executable, "src/main.py"])

def main():
    if len(sys.argv) < 2:
        print("Use: cfs [run|test]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test":
        run_tests()
    elif command == "run":
        if len(sys.argv) > 2:
            run_simulation(sys.argv[2])
        else:
            run_simulation()

    else:
        print(f"Command {command} not found.")
        print("Use: cfs [run|test]")
        sys.exit(1)

if __name__ == "__main__":
    main()
    