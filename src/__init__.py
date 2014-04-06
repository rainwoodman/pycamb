from core import PyCamb
from config import PARAMS

# for 0.1 compat
from compat import *

__doc__ = """ 
To use camb, define a PyCamb object with
  camb = PyCamb (**kwargs)

  the following **kwargs are accepted
  %s

""" % str(PARAMS)
