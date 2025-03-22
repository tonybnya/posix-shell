"""
Main application.
"""

import os
import shlex
import subprocess
import sys


def parser(input_: str) -> tuple[str, list[str]]:
    """
    Parser for the inputs entered in stdin.
    """
    prompt: list[str] = shlex.split(input_)
    cmd: str = prompt[0]
    args: list[str] = prompt[1:]

    return cmd, args


def redirect_stdout(command: str, sep: str) -> None:
    """
    Redirect stdout to a file
    """
    part1, to_file = command.split(sep)
    
    # Use shlex.split to handle multiple arguments properly
    args = shlex.split(part1)
    cmd = args[0]  # First part is the command
    
    try:
        # Run the command with all arguments and capture the output
        res = subprocess.run(args, capture_output=True, text=True)
        
        # Write the captured output to the file
        with open(to_file.strip(), "w", encoding="utf-8") as file:
            file.write(res.stdout)
            
        # If there's any error output, write it to stderr
        if res.stderr:
            sys.stderr.write(res.stderr)
            
    except FileNotFoundError as e:
        sys.stderr.write(f"{cmd}: {e.filename}: No such file or directory\n")


def main():
    """
    Definition of the main app.
    """
    builtins: list[str] = ["cd", "echo", "exit", "pwd", "type"]

    # uncomment this block to pass the first stage
    while True:
        sys.stdout.write("$ ")

        # wait for user input
        command = input()
        if command == "exit 0":
            # exit the program with status code 0
            sys.exit(0)
        elif " > " in command:
            sep = " > "
            redirect_stdout(command, sep)
        elif " 1> " in command:
            sep = " 1> "
            redirect_stdout(command, sep)
        elif command.startswith("echo"):
            # print the args
            if command.startswith("'") and command.endswith("'"):
                output = command[6:-1]
                print(output)
            else:
                parts = shlex.split(command[5:])
                print(" ".join(parts))
        elif command.startswith("type"):
            _, args = parser(command)
            # get the command to check
            cmd = args[0]
            # first check if command is a shell builtin
            if cmd in builtins:
                print(f"{cmd} is a shell builtin")
                command_in_path = True
            else:
                command_in_path = False
                # then check PATH for executable files
                for path in os.environ.get("PATH").split(":"):
                    try:
                        if os.path.exists(path) and cmd in os.listdir(path):
                            print(f"{cmd} is {path}/{cmd}")
                            command_in_path = True
                            break
                    except (
                        FileNotcommand_in_pathError,
                        PermissionError,
                        NotADirectoryError,
                    ):
                        # skip directories that don't exist or can't be accessed
                        continue

            if not command_in_path:
                print(f"{cmd}: not found")
        elif command == "pwd":
            print(os.getcwd())
        elif command.startswith("cd"):
            _, args = parser(command)
            if len(args) == 0:
                # cd without args should go to HOME
                target = os.environ.get("HOME", "")
            elif args[0] == "~":
                # cd ~ should go to HOME
                target = os.environ.get("HOME", "")
            else:
                target = args[0]
            try:
                os.chdir(target)
            except FileNotFoundError:
                print(f"cd: {target}: No such file or directory")
            except OSError as e:
                print(f"cd: {target}: {str(e)}")
        else:
            program = parser(command)
            prg, args = program

            # check if the command exists in PATH
            command_in_path = False
            for path in os.environ.get("PATH").split(":"):
                try:
                    if os.path.exists(path) and prg in os.listdir(path):
                        command_in_path = True
                        break
                except (FileNotFoundError, PermissionError, NotADirectoryError):
                    continue

            if not command_in_path:
                print(f"{prg}: command not found")
            else:
                try:
                    result = subprocess.run(
                        [prg] + args, capture_output=True, text=True
                    )
                    sys.stdout.write(result.stdout)
                    sys.stderr.write(result.stderr)
                except Exception as e:
                    print(f"Error executing command: {e}")


if __name__ == "__main__":
    main()
