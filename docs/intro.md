# Introduction to this awesome project

This can be the first of many documents in the `docs` folder,
that would compile into a nice "read the docs" website.

We use sphinx to generate the documentation, so we have to add that
into the `docs/requirements.txt` file. Note that this is a different file
than the top-level `requirements.txt` file.

In the `docs` folder, we also have a `conf.py` file, which is the configuration
for sphinx, and also an `index.rst` file, which is the root of the documentation
(i.e., has a list of the files that will be included in the documentation, and their ordering).

There are some other options to make sphinx generate documentation
based on the docstrings of the classes and functions, but I never got
around to learning how to do that.
