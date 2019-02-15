"""Testing of clyngor.decoder"""

from clyngor import solve, decode


ASP_GEN_CONCEPTS = """  % each model is a concept
% data
rel((a;b),(c;d)).
rel((b;e),(f;g)).
% generation of concepts
extent(X):- rel(X,_) ; rel(X,Y): intent(Y).
intent(Y):- rel(_,Y) ; rel(X,Y): extent(X).
:- not intent(_).  % must be populated
"""
ASP_LIST_CONCEPTS = """  % one model contains all concepts
concept(0).
extent(0,(a;b)). intent(0,(c;d)).
concept(1).
extent(1,(b;e)). intent(1,(f;g)).
concept(2).
extent(2,b). intent(2,(c;d;f;g)).
"""

class ConceptList:
    "Decoder used for tests inside that module using ASP_LIST_CONCEPTS"
    def __init__(self, concept:1, extent:all, intent:all):
        self.id = int(concept[0])
        self.extent = frozenset(arg for nb, arg in extent if nb == self.id)
        self.intent = frozenset(arg for nb, arg in intent if nb == self.id)
    def __eq__(self, othr):
        return all((
            self.id == othr.id,
            self.extent == othr.extent,
            self.intent == othr.intent
        ))
    def __hash__(self):  # ensure equivalence in set
        return hash(tuple(map(hash, (self.id, self.extent, self.intent))))
    def __repr__(self):  # help for debug
        return f"<{self.id}: {{{','.join(sorted(self.extent))}}} × {{{','.join(sorted(self.intent))}}}>"
    @staticmethod
    def expected():
        return {
            ConceptList([0], ([0, 'a'], [0, 'b']), ([0, 'c'], [0, 'd'])),
            ConceptList([1], ([1, 'b'], [1, 'e']), ([1, 'f'], [1, 'g'])),
            ConceptList([2], ([2, 'b'],), ([2, 'c'], [2, 'd'], [2, 'f'], [2, 'g'])),
        }
class ConceptGen(ConceptList):
    "Decoder used for tests inside that module using ASP_GEN_CONCEPTS"
    def __init__(self, extent:all, intent:all):
        self.id = 0  # just here to reuse Concept.List__eq__ (in a real setup, it would be autogenerated)
        self.extent = frozenset(arg for arg, in extent)
        self.intent = frozenset(arg for arg, in intent)
    @staticmethod
    def expected():
        return {
            ConceptGen((['a'], ['b']), (['c'], ['d'])),
            ConceptGen((['b'], ['e']), (['f'], ['g'])),
            ConceptGen((['b'],), (['c'], ['d'], ['f'], ['g'])),
        }

def test_Concept_classes():
    "just to ensure the important property of the object"
    assert ConceptList([0], ([0, 'a'],), ([0, 'c'],)) == ConceptList([0], ([0, 'a'],), ([0, 'c'],))
    assert ConceptGen((['a'],), (['c'],)) == ConceptGen((['a'],), (['c'],))

def test_decoder_list_concepts_per_decode():
    "All Concept in one model, first method: directly get decoded concepts"
    objects = set(decode(inline=ASP_LIST_CONCEPTS, decoders=[ConceptList]))
    assert objects == ConceptList.expected()

# def test_decoder_list_concepts_per_solve():
    # "All Concept in one model, second method: inside the solving scheme"
    # models = solve(inline=ASP_LIST_CONCEPTS, decoders=[ConceptList])
    # assert set(models.all_objects()) == ConceptList.expected()

def test_decoder_gen_concepts_per_decode():
    "One Concept per model, first method: directly get decoded concepts"
    objects = set(decode(inline=ASP_GEN_CONCEPTS, decoders=[ConceptGen]))
    assert objects == ConceptGen.expected()

# def test_decoder_gen_concepts_per_solve():
    # "One Concept per model, first method: inside the solving scheme"
    # models = solve(inline=ASP_GEN_CONCEPTS, decoders=[ConceptGen])
    # assert set(models.all_objects()) == ConceptGen.expected()
