from bitdeli.model import model, segment_model
from itertools import chain, imap
from collections import defaultdict

BIN_SIZES = (.1, .2)
LABELS = ('least active',
          'barely active',
          'moderately active',
          'very active',
          'most active')

LABELSET = {0: [],
            1: [4],
            2: [0, 4],
            3: [0, 2, 4],
            4: [0, 1, 3, 4],
            5: [0, 1, 2, 3, 4]}

def partition(lst, n, s):
    if n < len(lst):
        v = lst[n][0]
        m = len(lst)
        if n + 1 < m and lst[n + 1][0] == v:
            i = 0
            if s < 0:
                while n > 0 and v == lst[n - 1][0]:
                    n -= 1
            else:
                while n < m and v == lst[n][0]:
                    n += 1
        return lst[:n], lst[n:]
    else:
        return lst, []
    

def binify(profiles):
    counts = []
    for profile in profiles:
        all_events = chain.from_iterable(profile['events'].itervalues())
        counts.append((sum(count for hour, count in all_events), profile.uid))
    counts.sort()
    #counts = list(chain(*[[(i + 1, [])] * 10 for i in range(10)]))
    num_users = len(counts)
    rest = counts
    for i, bin_size in enumerate(BIN_SIZES):
        n = int(num_users * bin_size)
        for s in (1, -1):
            if rest:
                bin, rest = partition(rest[::s], n, s)
                rest = rest[::s]
                if bin:
                    yield bin
    if rest:
        yield rest

@model
def build(profiles):
    bins = list(sorted(binify(profiles), key=lambda x: x[0][0]))
    for label, bin in zip(LABELSET[len(bins)], bins):
        counts = frozenset(imap(lambda x: x[0], bin))
        key = '%d %d %s' % (min(counts), max(counts), LABELS[label])
        for count, uid in bin:
            yield key, uid

@segment_model
def segment(model, segments, labels):
    return namedtuple('SegmentInfo', ('model', 'segments', 'labels'))\
                     (model, segments, labels)