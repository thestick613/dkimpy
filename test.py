import unittest
import doctest
import dkim
from dkim.tests import test_suite

doctest.testmod(dkim)
unittest.TextTestRunner().run(test_suite())
