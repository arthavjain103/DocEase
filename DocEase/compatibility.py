"""
Compatibility fix for pdf2docx with Python 3.10+
This module patches the collections import issue in pdf2docx
"""

import sys
from collections import abc

# Patch collections.Iterable to point to collections.abc.Iterable
if sys.version_info >= (3, 10):
    import collections
    if not hasattr(collections, 'Iterable'):
        collections.Iterable = abc.Iterable
        collections.Mapping = abc.Mapping
        collections.MutableMapping = abc.MutableMapping
        collections.MutableSet = abc.MutableSet
        collections.MutableSequence = abc.MutableSequence
