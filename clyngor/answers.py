"""The Answers object"""


from collections import defaultdict
from clyngor import as_pyasp


class Answers:
    """Proxy to the solver, generated by solving methods like solve.solve
    or inline.ASP.

    Iterable on the answer sets generated by the solver.
    Also expose some answer set formatting tunning.

    """

    def __init__(self, answers:iter):
        """Answer sets must be iterable of (predicate, args)"""
        self._answers = iter(answers)
        self._first_arg_only = False
        self._group_atoms = False
        self._as_pyasp = False
        self._sorted = False


    @property
    def first_arg_only(self):
        self._first_arg_only = True
        return self

    @property
    def by_predicate(self):
        self._group_atoms = True
        return self

    @property
    def as_pyasp(self):
        self._as_pyasp = True
        return self

    @property
    def sorted(self):
        self._sorted = True
        return self


    def __iter__(self):
        """Yield answer sets"""
        sorted_tuple = lambda it: tuple(sorted(it))
        builder = sorted_tuple if self._sorted else frozenset
        for answer_set in self._answers:
            if self._first_arg_only:
                answer_set = builder((pred, args[0] if args else ())
                                       for pred, args in answer_set)
            else:
                answer_set = builder((pred, tuple(args))
                                       for pred, args in answer_set)
            # NB: as_pyasp flag behave diffrently if group_atoms is activated
            if self._group_atoms:
                mapping = defaultdict(set)
                for pred, args in answer_set:
                    if self._as_pyasp:
                        args = as_pyasp.Atom(pred, args)
                    mapping[pred].add(args)
                answer_set = {pred: builder(args)
                              for pred, args in mapping.items()}
            elif self._as_pyasp:
                answer_set = builder(as_pyasp.Atom(*atom) for atom in answer_set)
            yield answer_set


    def __next__(self):
        return next(iter(self))

