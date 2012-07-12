"""Software Transactional Memory and Observers"""

import weakref, sys, heapq, UserList, UserDict, sets
from peak.util.extremes import Max
from peak.util import decorators
try:
    import threading
except ImportError:
    import dummy_threading as threading

__all__ = [
    'STMHistory', 'AbstractSubject',  'Link', 'AbstractListener', 'Controller',
    'CircularityError', 'LocalController',
]


class CircularityError(Exception):
    """Rules arranged in an infinite loop"""


class AbstractSubject(object):
    """Abstract base for objects that can be linked via ``Link`` objects"""

    __slots__ = ()

    manager = None
    layer = 0

    def __init__(self):
        self.next_listener = None

    def iter_listeners(self):
        """Yield the listeners of this subject"""
        link = self.next_listener
        while link is not None:
            nxt = link.next_listener   # avoid unlinks breaking iteration
            ob = link()
            if ob is not None:
                yield ob
            link = nxt

class AbstractListener(object):
    """Abstract base for objects that can be linked via ``Link`` objects"""

    __slots__ = ()
    layer = 0

    def __init__(self):
        self.next_subject = None

    def iter_subjects(self):
        """Yield the listeners of this subject"""
        link = self.next_subject
        while link is not None:
            nxt = link.next_subject   # avoid unlinks breaking iteration
            if link.subject is not None:
                yield link.subject
            link = nxt

    def dirty(self):
        """Mark the listener dirty and query whether it should be scheduled

        If a true value is returned, the listener should be scheduled.  Note
        that this method is allowed to have side-effects, but must be
        idempotent.
        """
        return True

    def run(self):
        """Take whatever action the listener is supposed to take"""
        raise NotImplementedError











# Python 2.3 Compatibility

try:
    class Link(weakref.ref):
        pass

except TypeError:

    class link_base(object):
        __slots__ = 'weakref'

        def __new__(cls, ob, callback):
            self = object.__new__(cls)
            self.weakref = weakref.ref(ob, lambda r: callback(self))
            return self

        def __call__(self):
            return self.weakref()

else:
    link_base = weakref.ref


try:
    from threading import local
except ImportError:
    from _threading_local import local
    threading.local = local

try:
    set
except NameError:
    from sets import Set as set








class Link(link_base):
    """Dependency link"""
    __slots__ = [
        'subject','next_subject','prev_subject','next_listener','prev_listener'
    ]

    def __new__(cls, subject, listener):
        self = link_base.__new__(Link, listener, _unlink_fn)
        self.subject = self.prev_listener = subject
        self.prev_subject = None    # listener link is via weak ref
        nxt = self.next_subject = listener.next_subject
        if nxt is not None:
            nxt.prev_subject = self
        nxt = self.next_listener = subject.next_listener
        if nxt is not None:
            nxt.prev_listener = self
        listener.next_subject = self
        subject.next_listener = self
        return self

    def unlink(self):
        """Deactivate the link and remove it from its lists"""
        nxt = self.next_listener
        prev = self.prev_listener
        if nxt is not None:
            nxt.prev_listener = prev
        if prev is not None and prev.next_listener is self:
            prev.next_listener = nxt
        prev = self.prev_subject
        nxt = self.next_subject
        if nxt is not None:
            nxt.prev_subject = prev
        if prev is None:
            prev = self()   # get head of list
        if prev is not None and prev.next_subject is self:
            prev.next_subject = nxt
        self.subject = self.next_subject = self.prev_subject = None
        self.next_listener = self.prev_listener = None

_unlink_fn = Link.unlink

class STMHistory(object):
    """Simple STM implementation using undo logging and context managers"""

    active = in_cleanup = undoing = False

    def __init__(self):
        self.undo = []      # [(func,args), ...]
        self.at_commit =[]       # [(func,args), ...]
        self.managers = {}  # [mgr]->seq #  (context managers to __exit__ with)

    def atomically(self, func=lambda:None, *args, **kw):
        """Invoke ``func(*args,**kw)`` atomically"""
        if self.active:
            return func(*args, **kw)
        self.active = True
        try:
            try:
                retval = func(*args, **kw)
                self.cleanup()
                return retval
            except:
                self.cleanup(*sys.exc_info())
        finally:
            self.active = False

    def manage(self, mgr):
        assert self.active, "Can't manage without active history"
        if mgr not in self.managers:
            mgr.__enter__()
            self.managers[mgr] = len(self.managers)

    def on_undo(self, func, *args):
        """Call `func(*args)` if atomic operation is undone"""
        assert self.active, "Can't record undo without active history"
        if not self.undoing: self.undo.append((func, args))

    def savepoint(self):
        """Get a savepoint suitable for calling ``rollback_to()``"""
        return len(self.undo)


    def cleanup(self, typ=None, val=None, tb=None):
        # Exit the processing loop, unwinding managers
        assert self.active, "Can't exit when inactive"
        assert not self.in_cleanup, "Can't invoke cleanup while in cleanup"
        self.in_cleanup = True

        if typ is None:
            try:
                self.checkpoint()
            except:
                typ, val, tb = sys.exc_info()

        if typ is not None:
            try:
                self.rollback_to(0)
            except:
                typ, val, tb = sys.exc_info()

        managers = [(posn,mgr) for (mgr, posn) in self.managers.items()]
        managers.sort()
        self.managers.clear()
        try:
            while managers:
                try:
                    managers.pop()[1].__exit__(typ, val, tb)
                except:
                    typ, val, tb = sys.exc_info()
            if typ is not None:
                raise typ, val, tb
        finally:
            del self.at_commit[:], self.undo[:]
            self.in_cleanup = False
            typ = val = tb = None

    def change_attr(self, ob, attr, val):
        """Set `ob.attr` to `val`, w/undo log to restore the previous value"""
        self.on_undo(setattr, ob, attr, getattr(ob, attr))
        setattr(ob, attr, val)



    def rollback_to(self, sp=0):
        """Rollback to the specified savepoint"""
        assert self.active, "Can't rollback without active history"
        undo = self.undo
        self.undoing = True
        rb = self.rollback_to
        try:
            while len(undo) > sp:
                f, a = undo.pop()
                if f==rb and a:
                    sp = min(sp, a[0])
                else:
                    f(*a)
        finally:
            self.undoing = False

    def on_commit(self, func, *args):
        """Call `func(*args)` if atomic operation is committed"""
        assert self.active, "Not in an atomic operation"
        s = slice(len(self.at_commit), None)
        self.undo.append((self.at_commit.__delitem__, (s,)))
        self.at_commit.append((func, args))

    def checkpoint(self):
        """Invoke actions registered w/``on_commit()``, and clear the queue"""
        for (f,a) in self.at_commit:
            f(*a)
        del self.at_commit[:]













class Controller(STMHistory):
    """STM History with support for subjects, listeners, and queueing"""

    current_listener = destinations = routes = None
    readonly = False

    def __init__(self):
        super(Controller, self).__init__()
        self.reads = {}
        self.writes = {}
        self.has_run = {}   # listeners that have run
        self.layers = []    # heap of layer numbers
        self.queues = {}    # [layer]    -> dict of listeners to be run
        self.to_retry = {}

        from peak.events.trellis import Value
        self.pulse = Value(0)

    def checkpoint(self):
        self.has_run.clear()
        return super(Controller, self).checkpoint()

    def _retry(self):
        try:
            # undo back through listeners, watching to detect cycles
            self.destinations = set(self.to_retry)
            self.routes = {} # tree of rules that (re)triggered retry targets
            self.rollback_to(min([self.has_run[r] for r in self.to_retry]))
            for item in self.to_retry:
                if item in self.routes:
                    raise CircularityError(self.routes)
            else:
                map(self.schedule, self.to_retry)
        finally:
            self.to_retry.clear()
            self.destinations = self.routes = None





    def _unrun(self, listener, notified):
        destinations = self.destinations
        if destinations is not None:
            via = destinations.intersection(notified)
            if via:
                self.routes[listener] = via; destinations.add(listener)

    def run_rule(self, listener, initialized=True):
        """Run the specified listener"""
        if listener.layer is Max and not self.readonly:
            return self.with_readonly(self.run_rule, listener, initialized)

        old = self.current_listener
        self.current_listener = listener
        try:
            assert listener not in self.has_run,"Re-run of rule without retry"
            assert self.active, "Rules must be run atomically"
            if old is not None:
                assert not initialized,"Only un-initialized rules can be nested"
                old_reads, self.reads = self.reads, {}
                try:
                    listener.run()
                    self._process_reads(listener, initialized)
                finally:
                    self.reads = old_reads
            else:
                if initialized:
                    self.has_run[listener] = self.savepoint()
                    self.on_undo(self.has_run.pop, listener, None)

                try:
                    listener.run()
                    self._process_writes(listener)
                    self._process_reads(listener, initialized)
                except:
                    self.reads.clear()
                    self.writes.clear()
                    raise
        finally:
            self.current_listener = old
            
    def _process_writes(self, listener):
        #
        # Remove changed items from self.writes and notify their listeners,
        # and setting up an undo action to track this listener's participation
        # in any cyclic dependency that might occur later.
        #
        notified = {}
        writes = self.writes
        layer = listener.layer
        while writes:
            subject, writer = writes.popitem()
            for dependent in subject.iter_listeners():
                if dependent is not listener:
                    if dependent.dirty():
                        self.schedule(dependent, layer) #, writer
                        notified[dependent] = 1
        if notified:
            self.on_undo(self._unrun, listener, notified)

    def _process_reads(self, listener, undo=True):
        #
        # Remove subjects from self.reads and link them to `listener`
        # (Old subjects of the listener are deleted, and self.reads is cleared
        #
        subjects = self.reads

        link = listener.next_subject
        while link is not None:
            nxt = link.next_subject   # avoid unlinks breaking iteration
            if link.subject in subjects:
                del subjects[link.subject]
            else:
                if undo: self.undo.append((Link, (link.subject, listener)))
                link.unlink()
            link = nxt

        while subjects:
            link = Link(subjects.popitem()[0], listener)
            if undo: self.undo.append((link.unlink, ()))


    def schedule(self, listener, source_layer=None):
        """Schedule `listener` to run during an atomic operation

        If an operation is already in progress, it's immediately scheduled, and
        its scheduling is logged in the undo queue (unless it was already
        scheduled).

        If `source_layer` is specified, ensure that the listener belongs to
        a higher layer than the source, moving the listener from an existing
        queue layer if necessary.  (This layer elevation is intentionally
        NOT undo-logged, however.)
        """
        new = old = listener.layer
        get = self.queues.get

        assert not self.readonly or old is Max, \
            "Shouldn't be scheduling a non-Observer during commit"

        if source_layer is not None and source_layer >= listener.layer:
            new = source_layer + 1

        if listener in self.has_run:
            self.to_retry[listener]=1

        q = get(old)
        if q and listener in q:
            if new is not old:
                self.cancel(listener)
        elif self.active and not self.undoing:
            self.on_undo(self.cancel, listener)

        if new is not old:
            listener.layer = new
            q = get(new)

        if q is None:
             q = self.queues[new] = {listener:1}
             heapq.heappush(self.layers, new)
        else:
            q[listener] = 1

    def cancel(self, listener):
        """Prevent the listener from being recalculated, if applicable"""
        q = self.queues.get(listener.layer)
        if q and listener in q:
            del q[listener]
            if not q:
                del self.queues[listener.layer]
                self.layers.remove(listener.layer)
                self.layers.sort()  # preserve heap order

    def atomically(self, func=lambda:None, *args, **kw):
        """Invoke ``func(*args,**kw)`` atomically"""
        if self.active:
            return func(*args, **kw)
        return super(Controller,self).atomically(self._process, func, args, kw)

    def _process(self, func, args, kw):
        try:
            retval = func(*args, **kw)
            layers = self.layers
            queues = self.queues
            while layers or self.at_commit:
                self.pulse.value += 1
                while layers:
                    if self.to_retry:
                        self._retry()
                    q = queues[layers[0]]
                    if q:
                        listener = q.popitem()[0]
                        self.on_undo(self.schedule, listener)
                        self.run_rule(listener)
                    else:
                        del queues[layers[0]]
                        heapq.heappop(layers)
                self.checkpoint()
            return retval
        except:
            del self.layers[:]
            self.queues.clear()
            raise

    def lock(self, subject):
        assert self.active, "Subjects must be accessed atomically"
        manager = subject.manager
        if manager is not None and manager not in self.managers:
            self.manage(manager)

    def used(self, subject):
        self.lock(subject)
        cl = self.current_listener
        if cl is not None and subject not in self.reads:
            self.reads[subject] = 1
            if cl is not subject and subject.layer >= cl.layer:
                cl.layer = subject.layer + 1

    def changed(self, subject):
        self.lock(subject)
        cl = self.current_listener
        if cl is not None:
            self.writes[subject] = cl
        else:
            for listener in subject.iter_listeners():
                if listener.dirty():
                    self.schedule(listener)
        if self.readonly and subject is not cl:
            raise RuntimeError("Can't change objects during @perform or @compute")

    def initialize(self, listener):
        self.run_rule(listener, False)

    def with_readonly(self, func, *args):
        if self.readonly:
            return func(*args)
        else:
            self.readonly = True
            try:     return func(*args)
            finally: self.readonly = False

class LocalController(Controller, threading.local):
    """Thread-local Controller"""


