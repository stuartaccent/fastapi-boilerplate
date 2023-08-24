import os

# replace the db url with the test one
# originally was in the conftest.py file but had to ensure
# it was always before any import, it kept wiping the local db when
# it wasn't. Here it can be forgotten about
if os.environ.get("TEST_DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
