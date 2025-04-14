import os

def run_command(command):
    result = os.system(command=command)
    return result