#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

# Run setup.py to install IdleISS
echo "Installing IdleISS"
pip install -e .[dev]

# Run tests
echo "Running Tests"
nosetests

# Run Base App with no interpreter
echo "Running IdleISS"
idleiss -q

# Run Example Combat Sim
echo "Running Combat Sim"
idleiss --simulate-battle config/Example_Fleet_Fight.json

# Run with interpreter with pre-set instructions
echo "Running Sample Interpreter"
idleiss --preload interpreter_test_log.txt
