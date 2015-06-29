"""
This module provides a RangeSet data structure. A range set is, as the
name implies, a set of ranges. Intuitively, you could think about a
range set as a subset of the real number line, with arbitrary gaps.
Some examples of range sets on the real number line:

1. -infinity to +infinity
2. -1 to 1
3. 1 to 4, 10 to 20
4. -infinity to 0, 10 to 20
5. (the empty set)

The code lives on github at: https://github.com/axiak/py-rangeset.

Overview
-------------

.. toctree::
   :maxdepth: 2


The rangeset implementation offers immutable objects that represent the range
sets as described above. The operations are largely similar to the
`set object <http://docs.python.org/library/stdtypes.html#set>`_ with the
obvious exception that mutating methods such as ``.add`` and ``.remove``
are not available. The main object is the ``RangeSet`` object.
"""

import bisect
import operator
import functools
import collections

__version__ = (0, 0, 6)

__all__ = ('INFINITY', 'NEGATIVE_INFINITY',
           'RangeSet')

_parent = collections.namedtuple('RangeSet_', ['ends'])

class _Indeterminate(object):
    def timetuple(self):
        return ()
    def __eq__(self, other):
        return other is self

class _Infinity(_Indeterminate):
    def __lt__(self, other):
        return False
    def __gt__(self, other):
        return True
    def __str__(self):
        return 'inf'
    __repr__ = __str__

class _NegativeInfinity(_Indeterminate):
    def __lt__(self, other):
        return True
    def __gt__(self, other):
        return False
    def __str__(self):
        return '-inf'
    __repr__ = __str__

INFINITY = _Infinity()
NEGATIVE_INFINITY = _NegativeInfinity()

class RangeSet(_parent):
    def __new__(cls, start, end):
        if end is _RAW_ENDS:
            ends = start
        else:
            if isinstance(start, _Indeterminate) and isinstance(end, _Indeterminate) and \
                    start == end:
                raise LogicError("A range cannot consist of a single end the line.")
            if start > end:
                start, end = end, start
            ends = ((start, _START), (end, _END))
        return _parent.__new__(cls, ends)

    def __merged_ends(self, *others):
        sorted_ends = list(self.ends)
        for other in others:
            sorted_ends.extend(RangeSet.__coerce(other).ends)
        sorted_ends.sort()
        return sorted_ends

    @classmethod
    def __coerce(cls, value):
        if isinstance(value, RangeSet):
            return value
        elif isinstance(value, tuple) and len(value) == 2:
            return cls(value[0], value[1])
        else:
            return cls.mutual_union(*[(x, x) for x in value])

    @classmethod
    def __iterate_state(cls, ends):
        state = 0
        for _, end in ends:
            if end == _START:
                state += 1
            else:
                state -= 1
            yield _, end, state

    def __or__(self, *other):
        sorted_ends = self.__merged_ends(*other)
        new_ends = []
        for _, end, state in RangeSet.__iterate_state(sorted_ends):
            if state > 1 and end == _START:
                continue
            elif state > 0 and end == _END:
                continue
            new_ends.append((_, end))
        return RangeSet(tuple(new_ends), _RAW_ENDS)

    union = __or__

    def __and__(self, *other, **kwargs):
        min_overlap = kwargs.pop('minimum', 2)
        if kwargs:
            raise ValueError("kwargs is not empty: {0}".format(kwargs))
        sorted_ends = self.__merged_ends(*other)
        new_ends = []
        for _, end, state in RangeSet.__iterate_state(sorted_ends):
            if state == min_overlap and end == _START:
                new_ends.append((_, end))
            elif state == (min_overlap - 1) and end == _END:
                new_ends.append((_, end))
        return RangeSet(tuple(new_ends), _RAW_ENDS)

    intersect = __and__

    def __ror__(self, other):
        return self.__or__(other)

    def __rand__(self, other):
        return self.__and__(other)

    def __rxor__(self, other):
        return self.__xor__(other)

    def __xor__(self, *other):
        sorted_ends = self.__merged_ends(*other)
        new_ends = []
        old_val = None
        for _, end, state in RangeSet.__iterate_state(sorted_ends):
            if state == 2 and end == _START:
                new_ends.append((_, _NEGATE[end]))
            elif state == 1 and end == _END:
                new_ends.append((_, _NEGATE[end]))
            elif state == 1 and end == _START:
                new_ends.append((_, end))
            elif state == 0 and end == _END:
                new_ends.append((_, end))
        return RangeSet(tuple(new_ends), _RAW_ENDS)

    symmetric_difference = __xor__

    def __contains__(self, test):
        last_val, last_end = None, None
        if not self.ends:
            return False
        if isinstance(test, _Indeterminate):
            return False
        for _, end, state in RangeSet.__iterate_state(self.ends):
            if _ == test:
                return True
            elif last_val is not None and _ > test:
                return last_end == _START
            elif _ > test:
                return False
            last_val, last_end = _, end
        return self.ends[-1][0] == test

    def issuperset(self, test):
        if isinstance(test, RangeSet):
            rangeset = test
        else:
            rangeset = RangeSet.__coerce(test)
        difference = rangeset - ~self
        return difference == rangeset

    __ge__ = issuperset

    def __gt__(self, other):
        return self != other and self >= other

    def issubset(self, other):
        return RangeSet.__coerce(other).issuperset(self)

    __le__ = issubset

    def __lt__(self, other):
        return self != other and self <= other

    def isdisjoint(self, other):
        return not bool(self & other)

    def __nonzero__(self):
        return bool(self.ends)

    def __invert__(self):
        if not self.ends:
            new_ends = ((NEGATIVE_INFINITY, _START),
                        (INFINITY, _END))
            return RangeSet(new_ends, _RAW_ENDS)
        new_ends = list(self.ends)
        head, tail = [], []
        if new_ends[0][0] == NEGATIVE_INFINITY:
            new_ends.pop(0)
        else:
            head = [(NEGATIVE_INFINITY, _START)]
        if new_ends[-1][0] == INFINITY:
            new_ends.pop(-1)
        else:
            tail = [(INFINITY, _END)]
        for i, value in enumerate(new_ends):
            new_ends[i] = (value[0], _NEGATE[value[1]])
        return RangeSet(tuple(head + new_ends + tail), _RAW_ENDS)


    invert = __invert__

    def __sub__(self, other):
        return self & ~RangeSet.__coerce(other)

    def difference(self, other):
        return self.__sub__(other)

    def __rsub__(self, other):
        return RangeSet.__coerce(other) - self

    def measure(self):
        if not self.ends:
            return 0
        if isinstance(self.ends[0][0], _Indeterminate) or isinstance(self.ends[-1][0], _Indeterminate):
            raise ValueError("Cannot compute range with unlimited bounds.")
        return reduce(operator.add, (self.ends[i + 1][0] - self.ends[i][0] for i in range(0, len(self.ends), 2)))

    def range(self):
        if not self.ends:
            return 0
        if isinstance(self.ends[0][0], _Indeterminate) or isinstance(self.ends[-1][0], _Indeterminate):
            raise ValueError("Cannot compute range with unlimited bounds.")
        return self.ends[-1][0] - self.ends[0][0]

    def __str__(self):
        pieces = ["{0} -- {1}".format(self.ends[i][0], self.ends[i + 1][0])
                                    for i in range(0, len(self.ends), 2)]
        return "<RangeSet {0}>".format(", ".join(pieces))

    __repr__ = __str__

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, RangeSet):
            try:
                other = RangeSet.__coerce(other)
            except TypeError:
                return False
        return self.ends == other.ends

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.ends)

    @classmethod
    def mutual_overlaps(cls, *ranges, **kwargs):
        minimum = kwargs.pop('minimum', 2)
        if kwargs:
            raise ValueError("kwargs is not empty: {0}".format(kwargs))
        return cls.__coerce(ranges[0]).intersect(*ranges[1:], minimum=minimum)

    @classmethod
    def mutual_union(cls, *ranges):
        return cls.__coerce(ranges[0]).union(*ranges[1:])

    @property
    def min(self):
        return self.ends[0][0]

    @property
    def max(self):
        return self.ends[-1][0]

    def __iter__(self):
        ends_copy = list(self.ends)
        for i in range(0, len(ends_copy), 2):
            yield (ends_copy[i][0], ends_copy[i + 1][0])

_START = -1
_END = 1

_NEGATE = {_START: _END, _END: _START}

_RAW_ENDS = object()


class LogicError(ValueError):
    pass
