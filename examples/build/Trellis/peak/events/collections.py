import trellis, bisect
from peak.util import decorators
from trellis import set
from new import instancemethod

__all__ = [
    'SortedSet', 'SubSet', 'Observing', 'Hub'
]


class SubSet(trellis.Set):
    """Set that's constrained to be a subset of another set"""

    base = trellis.make(trellis.Set, writable=True)

    trellis.compute()
    def added(self):
        base = self.base
        return set([item for item in self._added if item in base])

    trellis.compute()
    def removed(self):
        base = self.base
        if self.base.removed:
            # XXX need to filter this by self._data somehow
            return set(self._removed) | set(self.base.removed)
        else:
            return self._removed













class Hub(trellis.Component):
    """Pub/sub messaging"""

    def get(self, *rule):
        """Return messages of same length with matching non-``None`` args"""
        return self._queries[rule].value

    def put(self, *row):
        """Send a message to any active subscribers"""
        self._inputs.append(row)

    _queries = trellis.cellcache(lambda self,key:(), resetting_to=())
    _inputs = trellis.make(trellis.Pipe)
    _index = trellis.make(dict)     # {(pos,value):{rule:1}}}

    _queries.connector()
    def _add_rule(self, rule):
        key = None
        for pv in enumerate(rule):
            if pv[1] is not None:
                key = pv
        if key is not None:
            ind = self._index.setdefault(key, {})
            ind[rule] = 1
            trellis.on_undo(ind.pop, rule, 1)

    _queries.disconnector()
    def _del_rule(self, rule):
        index = self._index
        for pv in enumerate(rule):
            if pv in index:
                index[pv].pop(rule, 1)
                trellis.on_undo(index[pv].__setitem__, rule, 1)
                







    trellis.maintain()
    def _notify(self):
        """Send received rows to observers"""

        inputs = self._inputs
        if not inputs:
            return      # nothing to see, move along...

        index = self._index
        matches = {}

        for row in inputs:
            for pv in enumerate(row):
                if pv not in index:
                    continue
                for rule in index[pv]:
                    if len(rule)==len(row):
                        for v1,v2 in zip(rule, row):
                            if v1!=v2 and v1 is not None:
                                break
                        else:
                            matches.setdefault(rule,[]).append(row)
        if matches:
            queries = self._queries
            for rule in matches:
                queries[rule].receive(matches[rule])















class Observing(trellis.Component):
    """Monitor a set of keys for changes"""

    lookup_func = trellis.attr(lambda x:x)
    keys = trellis.make(trellis.Set)

    trellis.maintain()
    def _watching(self):
        cells = self._watching or {}
        for k in self.keys.removed:
            if k in cells:
                trellis.on_undo(cells.__setitem__, k, cells[k])
                del cells[k]
                trellis.mark_dirty()
        lookup = self.lookup_func
        for k in self.keys.added:
            trellis.on_undo(cells.pop, k, None)
            cells[k] = trellis.Cell(instancemethod(lookup, k, type(k)))
            trellis.mark_dirty()
        return cells

    trellis.maintain(initially=({}, {}))
    def watched_values(self):
        forget, old = self.watched_values
        lookup = self.lookup_func
        return old, dict([(k, v.value) for k,v in self._watching.iteritems()])
        
    trellis.maintain(resetting_to={})
    def changes(self):
        old, current = self.watched_values
        changes = {}
        if old!=current:
            for k,v in current.iteritems():
                if k not in old or v!=old[k]:
                    changes[k] = v, old.get(k, v)
        return changes





class SortedSet(trellis.Component):
    """Represent a set as a list sorted by a key"""

    trellis.attrs(
        sort_key  = lambda x:x,  # sort on the object
        reverse = False,
        items = None,
        old_key = None,
        old_reverse = None
    )
    data    = trellis.make(trellis.Set, writable=True)
    changes = trellis.attr(resetting_to=[])

    def __getitem__(self, key):
        if self.reverse:
            key = -(key+1)
        return self.items[int(key)][1]

    def __len__(self):
        return len(self.items)

    trellis.maintain()
    def state(self):
        key, reverse = self.sort_key, self.reverse
        data = self.items
        if key != self.old_key or reverse != self.old_reverse:
            if data is None or key != self.old_key:
                data = [(key(ob),ob) for ob in self.data]
                data.sort()
                self.items = data
            size = len(self.data)
            self.changes = [(0, size, size)]
            self.old_key = key
            self.old_reverse = reverse
        else:
            self.changes = self.compute_changes(key, data, reverse)

    def __repr__(self):
        return repr(list(self))


    def compute_changes(self, key, items, reverse):
        changes = [
            (key(ob), "+", ob) for ob in self.data.added] + [
            (key(ob), "-", ob) for ob in self.data.removed
        ]
        changes.sort()
        changes.reverse()

        lo = 0
        hi = old_size = len(items)
        regions = []
        

        for k, op, ob in changes:
            ind = (k, ob)
            if lo<hi and items[hi-1][0]>=ind:
                pos = hi-1    # shortcut
            else:
                pos = bisect.bisect_left(items, ind, lo, hi)

            if op=='-':
                del items[pos]
                if regions and regions[-1][0]==pos+1:
                    regions[-1] = (pos, regions[-1][1], regions[-1][2])
                else:
                    regions.append((pos, pos+1, 0))
            else:
                items.insert(pos, ind)
                if regions and regions[-1][0]==pos:
                    regions[-1] = (pos, regions[-1][1], regions[-1][2]+1)
                else:
                    regions.append((pos, pos, 1))
            hi=pos

        if reverse:
            return [(old_size-e, old_size-s, sz) for (s,e,sz) in regions[::-1]]
        return regions




