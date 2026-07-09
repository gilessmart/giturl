from .cli import main

# This is the execution path used when the app is invoked with `python -m giturl`,
# which is how the VSCode debugger invokes it.
# It would be possible for the debugger to run the script ([project.scripts]),
# and not have this file, except that wouldn't work in Windows because on Windows pip
# generates an .exe file in the venv instead of a plain script.
if __name__ == "__main__":
    main()
