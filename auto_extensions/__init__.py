import os
import glob

__all__ = [os.path.split(f)[-1].replace(".py", "") for f in glob.glob(os.path.dirname(os.path.realpath(__file__)) +
                                                                      "/*.py") if "__init__.py" not in f]

