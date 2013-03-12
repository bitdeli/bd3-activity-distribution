from bitdeli.insight import insight, segment, segment_label
from bitdeli.widgets import Text, Table
from discodb.query import Q, Literal, Clause
from collections import namedtuple

CAPTION = """
## What is the proportion of active users compared to inactive users?
"""

LABEL = """
### **{label}** ({size:,} users)
"""

COLORS = {'least active': 'rgb(255, 36, 0)',
          'barely active': 'rgb(255, 197, 11)',
          'moderately active': 'rgb(179, 220, 108)',
          'very active': 'rgb(0, 163, 89)',
          'most active': 'rgb(118, 192, 255)'}

def table_data(model, counter):
    def num(x):
        return '{0:,}'.format(int(x))
    keys = sorted(model, key=lambda x: int(x.split()[0]))
    sizes = [counter(model, key) for key in keys]
    total = float(sum(sizes))
    for i, (key, size) in enumerate(zip(keys, sizes)):
        mi, ma, label = key.split(' ', 2)
        crange = num(mi) if mi == ma else '%s-%s' % (num(mi), num(ma))
        txt = crange + (' event' if crange == '1' else ' events')
        perc = '%.1f%%' % (100. * size / total)
        yield 'c%d' % i, txt, label, size, perc, key

def make_table(model, counter):
    data = list(table_data(model, counter))
    def columns():
        for col, txt, label, size, perc, key in data:
            if size:
                yield {'name': col,
                       'label': label.capitalize(),
                       'width': perc,
                       'sortable': False,
                       'cell': 'markdown'}
    def row():
        for col, txt, label, size, perc, key in data:
            if size:
                yield col, {'label': '*%s*\n\n'
                                     '**%s** (%s) users' % (txt, perc, size),
                            'background': COLORS[label],
                            'segment_id': key}
    return Table(size=(12, 2),
                 fixed_width=False,
                 data={'columns': list(columns()), 'rows': [dict(row())]})
    
@insight
def view(model, params):
    def test_segment():
        import random
        random.seed(21)
        labels = ['First Segment'] #, 'Second']
        segments = [frozenset(random.sample(model.unique_values(), 100))]
                    #frozenset(random.sample(model.unique_values(), 200))]
        return namedtuple('SegmentInfo', ('model', 'segments', 'labels'))\
                         (model, segments, labels)
        
    #model = test_segment()
    has_segments = hasattr(model, 'segments')
    omodel = model.model if has_segments else model
    
    yield Text(size=(12, 'auto'),
               label='Showing user activity',
               data={'text': CAPTION})
    yield Text(size=(12, 'auto'),
               data={'text': LABEL.format(label='All users',
                                          size=len(omodel.unique_values()))})
    yield make_table(omodel, lambda model, key: len(model[key]))
    
    if has_segments:
        for segment, label in zip(model.segments, model.labels):
            def segcounter(model, key):
                return sum(1 for uid in model[key] if uid in segment)
            yield Text(size=(12, 'auto'),
                       data={'text': LABEL.format(label=label,
                                                  size=len(segment))})
            yield make_table(model.model, segcounter)
    
@segment
def segment(model, params):
    return model[params['value']['segment_id']]
    
@segment_label
def label(segment, params):
    label = params['value']['segment_id'].split(' ', 2)[2]
    return '%s users' % label.capitalize()

    