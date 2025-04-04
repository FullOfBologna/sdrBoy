from Registers import *
import inspect
import sys
# import unittest
import pytest
import CPU
import Memory
from utils import *

def main():
    print("Running Test Cases...")
    exit_code = pytest.main(['tests/']) # Example: run tests verbosely
    print(f"Pytest finished with exit code: {exit_code}")
    
    # Exit with the pytest status code
    sys.exit(int(exit_code))

if __name__ == '__main__':
    main()