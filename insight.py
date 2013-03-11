from bitdeli.insight import insight, segment, segment_label
from bitdeli.widgets import Text, Table
from discodb.query import Q, Literal, Clause

CAPTION = """
### What is the proportion of active users compared to inactive users?
"""

COLORS = {'least active': 'rgb(255, 36, 0)',
          'barely active': 'rgb(255, 197, 11)',
          'moderately active': 'rgb(179, 220, 108)',
          'very active': 'rgb(0, 163, 89)',
          'most active': 'rgb(118, 192, 255)'}

def keys(model):
    for i, key in enumerate(sorted(model.keys(), key=lambda x: int(x.split('-')[0]))):
        yield 'c%d' % i, key.split(' ', 2)

def columns(model):
    for col, (counts, perc, label) in keys(model):
        yield {'name': col,
               'label': label.capitalize(),
               'width': perc,
               'sortable': False,
               'cell': 'markdown'}
    
def rows(model):
    def num(x):
        return '{0:,}'.format(int(x))
    def row():
        for col, (counts, perc, label) in keys(model):
            key = ' '.join((counts, perc, label))
            n = num(len(model[key]))
            mi, ma = map(num, counts.split('-'))
            crange = str(mi) if mi == ma else '%s-%s' % (mi, ma)
            txt = crange + (' event' if crange == '1' else ' events')
            yield col, {'label': '*%s*\n\n'
                                 '**%s** (%s) users' % (txt, perc, n),
                        'background': COLORS[label],
                        'segment_id': key}
    yield dict(row())

@insight
def view(model, params):
    yield Text(size=(12, 'auto'),
               label="Showing user activity",
               data={'text': CAPTION})
    yield Table(size=(12, 3),
                fixed_width=False,
                data={'columns': list(columns(model)),
                      'rows': list(rows(model))})
    
@segment
def segment(model, params):
    return model[params['segment_id']]
    
@segment_label
def label(segment, params):
    return '%s users' % params['segment_id'].split(' ', 2)[2].capitalize()
    