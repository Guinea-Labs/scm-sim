# scm-sim

$ cd your-python-project
$ python -m venv .venv
# Activate your environment with:
#      `source .venv/bin/activate` on Unix/macOS
# or   `.venv\Scripts\activate` on Windows
# and remember to deactivate when done with `deactivate`




# ignore this portion for now. we don't proper packaging set up and don't really need it.
$ pip install -e .

# Now you have access to your package
# as if it was installed in .venv
$ python -c "import your_python_project"