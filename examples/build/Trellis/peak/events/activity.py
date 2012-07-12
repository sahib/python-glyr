from peak import context
from peak.events import trellis, stm
from peak.util import addons, decorators, symbols
from peak.util.extremes import Min, Max
import heapq, time, sys

__all__ = [
    'Time', 'EPOCH', 'NOT_YET', 'EventLoop', 'WXEventLoop', 'TwistedEventLoop',
    'task', 'resume', 'Pause', 'Return', 'TaskCell',
]

try:
    set
except NameError:
    from sets import Set as set
        

























class _Timer(object):
    """Value representing a moment in time"""

    __slots__ = '_when'

    def __init__(self, _when):
        self._when = _when

    def __getitem__(self, interval):
        """Get a timer that's offset from this one by `interval` seconds"""
        if self is NOT_YET: return self
        return _Timer(self._when + interval)

    def __sub__(self, other):
        """Get the interval in seconds between two timers"""
        if not isinstance(other, _Timer):
            raise TypeError("Can't subtract %r from timer" % (other,))
        return self._when - other._when

    def __eq__(self, other):
        if not isinstance(other, _Timer):
            return False
        return self._when == other._when

    def __ne__(self, other):
        return not self==other

    def __ge__(self, other):
        return not self < other

    def __nonzero__(self):
        return Time.reached(self)

    def __lt__(self, other):
        if not isinstance(other, _Timer):
            raise TypeError # for now
        return self._when < other._when

    def __hash__(self):
        return hash(self._when)

    def begins_with(self, flag):
        """Keep track of the moment when `flag` first becomes true"""
        if flag:
            return min(self, Time[0])
        return NOT_YET

EPOCH = _Timer(0)
NOT_YET = _Timer(Max)
    
































class EventLoop(trellis.Component, context.Service):
    """Run an application event loop"""
    trellis.attrs(
        running = False,
        stop_requested = False,
    )

    _call_queue = trellis.make(list, writable=True)
    _next_time = trellis.compute(lambda self: Time.next_event_time(True))

    _callback_active = initialized = False

    def run(self):
        """Loop updating the time and invoking requested calls"""
        assert not self.running, "EventLoop is already running"
        assert not trellis.ctrl.active, "Event loop can't be run atomically"
        self.call(lambda:None)
        self.stop_requested = False
        self.running = True
        try:
            Time.tick()
            self._loop()
            self.stop()
        finally:
            self._tearDown()
            
    def stop(self):
        """Stop the event loop at the next opportunity"""
        assert self.running, "EventLoop isn't running"
        self.stop_requested = True

    decorators.decorate(trellis.modifier)
    def call(self, func, *args, **kw):
        """Call `func(*args, **kw)` at the next opportunity"""
        self._call_queue.append((func, args, kw))
        if not self.initialized:
            self._setup()
            self.initialized = True
        trellis.on_undo(self._call_queue.pop)
        self._callback_if_needed()

    def poll(self):
        """Execute up to a single pending call"""
        self.flush(1)

    def flush(self, count=0):
        """Execute the specified number of pending calls (0 for all)"""
        assert not trellis.ctrl.active, "Event loop can't be run atomically"
        queue = self._split_queue(count)
        for (f, args, kw) in queue:
            f(*args, **kw)
        self._callback_if_needed()
        if Time.auto_update:
            Time.tick()                                        
        else:
            Time.advance(self._next_time or 0)

    decorators.decorate(trellis.modifier)
    def _callback_if_needed(self):
        if self._call_queue and not self._callback_active:
            self._arrange_callback(self._callback)
            self._callback_active = True
        
    decorators.decorate(trellis.modifier)
    def _split_queue(self, count):
        queue = self._call_queue
        count = count or len(queue)
        if queue:
            head, self._call_queue = queue[:count], queue[count:]
            return head
        return ()

    decorators.decorate(trellis.modifier)
    def _tearDown(self):
        self.running = False
        self.stop_requested = False

    def _callback(self):
        self._callback_active = False
        self.flush(1)


    def _loop(self):
        """Subclasses should invoke their external loop here"""
        queue = self._call_queue
        while (queue or self._next_time) and not self.stop_requested:
            self.flush(1)

    def _setup(self):
        """Subclasses should import/setup their external loop here

        Note: must be inherently thread-safe, or else use a cell attribute in
        order to benefit from locking.  This method is called atomically, but
        you should not log any undo actions."""

    def _arrange_callback(self, func):
        """Subclasses should register `func` to be called by external loop

        Note: Must be safe to call this from a 'foreign' thread."""
























class TwistedEventLoop(EventLoop):
    """Twisted version of the event loop"""

    context.replaces(EventLoop)    
    reactor = _delayed_call = None

    trellis.perform()
    def _ticker(self):
        if self.running:
            if Time.auto_update:
                if self._next_time is not None:
                    if self._delayed_call and self._delayed_call.active():
                        self._delayed_call.reset(self._next_time)
                    else:
                        self._delayed_call = self.reactor.callLater(
                            self._next_time, Time.tick
                        )
            if self.stop_requested:
                self.reactor.stop()

    def _loop(self):
        """Loop updating the time and invoking requested calls"""
        self.reactor.run()

    def _arrange_callback(self, func):
        self.reactor.callLater(0, func)

    def _setup(self):
        from twisted.internet import reactor
        self.reactor = reactor











class WXEventLoop(EventLoop):
    """wxPython version of the event loop

    This isn't adequately tested; the wx event loop is completely hosed when
    it comes to running without any windows, so it's basically impossible to
    unit test without mocking 'wx' (which I haven't tried to do.  Use at your
    own risk.  :(
    """
    context.replaces(EventLoop)    
    wx = None

    trellis.perform()
    def _ticker(self):
        if self.running:
            if Time.auto_update:
                if self._next_time is not None:
                    self.wx.FutureCall(self._next_time*1000, Time.tick)
            if self.stop_requested:
                self.wx.GetApp().ExitMainLoop()

    def _loop(self):
        """Loop updating the time and invoking requested calls"""
        app = self.wx.GetApp()
        assert app is not None, "wx.App not created"
        while not self.stop_requested:
            app.MainLoop()
            if app.ExitOnFrameDelete:   # handle case where windows exist
                self.stop()
            else:
                app.ProcessPendingEvents()  # ugh

    def _arrange_callback(self, func):
        """Call `func(*args, **kw)` at the next opportunity"""
        self.wx.CallAfter(func)
            
    def _setup(self):
        import wx
        self.wx = wx



class Time(trellis.Component, context.Service):
    """Manage current time and intervals"""

    _now = EPOCH._when
    auto_update = trellis.attr(True)
    _schedule = trellis.make(lambda self: [Max], writable=True)
    _events = trellis.cellcache(lambda self, key: False)

    _events.connector()
    def _add_event(self, when):
        # this heappush doesn't need an undo, since _updated() ignores extras
        heapq.heappush(self._schedule, when)
        trellis.changed(trellis.Cells(self)['_schedule'])

    _events.disconnector()
    def _del_event(self, when):
        pass

    trellis.maintain()
    def _updated(self):
        schedule = self._schedule
        while self._tick >= schedule[0]:
            key = heapq.heappop(schedule)
            trellis.on_undo(heapq.heappush, schedule, key)
            if key in self._events:
                self._events[key].receive(True)
    
    def reached(self, timer):
        when = timer._when
        return self._now >= when or (
            trellis.ctrl.current_listener is not None
            and self._events[when].value
        )

    def __getitem__(self, interval):
        """Return a timer that's the given offset from the current time"""
        return _Timer(self._now + interval)




    def advance(self, interval):
        """Advance the current time by the given interval"""
        self._set(self._now + interval)

    def tick(self):
        """Update current time to match ``time.time()``"""
        self._set(self.time())

    def _set(self, when):
        trellis.change_attr(self, '_now', when)
        self._tick = when
    _set = trellis.modifier(_set)

    trellis.maintain(initially=EPOCH._when)
    def _tick(self):
        if self.auto_update:
            tick = self._now = self.time()            
            trellis.poll()
            return tick
        return self._tick

    def next_event_time(self, relative=False):
        """The time of the next event to occur, or ``None`` if none scheduled

        If `relative` is True, returns the number of seconds until the event;
        otherwise, returns the absolute ``time.time()`` of the event.
        """
        now = self._tick   # ensure recalc whenever time moves forward
        when = self._schedule[0]
        if when is Max:
            return None
        if relative:
            return when - now
        return when

    def time(self): return time.time()





class TaskCell(trellis.AbstractCell, stm.AbstractListener):
    """Cell that manages a generator-based task"""
    
    __slots__ = (
        '_result', '_error', '_step', 'next_subject', 'layer', '_loop',
        '_scheduled', '__weakref__',
    )

    def __init__(self, func):
        self._step = self._stepper(func)
        self.layer = 0
        self.next_subject = None
        self._loop = EventLoop.get()
        self._scheduled = False
        trellis.atomically(self.dirty)

    def dirty(self):
        if not self._scheduled:
            trellis.change_attr(self, '_scheduled', True)
            trellis.on_commit(self._loop.call, trellis.atomically, self.do_run)
        return False

    decorators.decorate(classmethod)
    def from_attr(cls, rule, value, discrete):
        return cls(rule)
















    def _stepper(self, func):
        VALUE = self._result = []
        ERROR = self._error  = []               
        STACK = [func()]
        CALL = STACK.append
        RETURN = STACK.pop
        ctrl = trellis.ctrl
        def _step():
            while STACK:
                try:
                    it = STACK[-1]
                    if VALUE and hasattr(it, 'send'):
                        rv = it.send(VALUE[0])
                    elif ERROR and hasattr(it, 'throw'):
                        rv = it.throw(*ERROR.pop())
                    else:
                        rv = it.next()
                except:
                    del VALUE[:]
                    ERROR.append(sys.exc_info())
                    if ERROR[-1][0] is StopIteration:
                        ERROR.pop() # not really an error
                    RETURN()
                else:
                    del VALUE[:]
                    if rv is Pause:
                        break
                    elif hasattr(rv, 'next'):
                        CALL(rv); continue
                    elif isinstance(rv, Return):
                        rv = rv.value
                    VALUE.append(rv)
                    if len(STACK)==1: break
                    RETURN()
            if STACK and not ERROR and not ctrl.reads:
                ctrl.current_listener.dirty() # re-run if still running
            return resume()

        return _step


    def do_run(self):
        trellis.change_attr(self, '_scheduled', False)
        ctrl = trellis.ctrl
        ctrl.current_listener = self
        try:
            try:
                self._step()
                # process writes as if from a non-rule perspective
                writes = ctrl.writes
                has_run = ctrl.has_run.get
                while writes:
                    subject, writer = writes.popitem()
                    for dependent in subject.iter_listeners():
                        if has_run(dependent) is not self:
                            if dependent.dirty():
                                ctrl.schedule(dependent)

                # process reads in normal fashion
                ctrl._process_reads(self)

            except:
                ctrl.reads.clear()
                ctrl.writes.clear()
                raise           
        finally:
            ctrl.current_listener = None

Pause = symbols.Symbol('Pause', __name__)

decorators.struct()
def Return(value):
    """Wrapper for yielding a value from a task"""
    return value,








def resume():
    """Get the result of a nested task invocation (needed for Python<2.5)"""
    c = trellis.ctrl.current_listener
    if not isinstance(c, TaskCell):
        raise RuntimeError("resume() must be called from an @activity.task")
    elif c._result:
        return c._result[0]
    elif c._error:
        e = c._error.pop()
        try:
            raise e[0], e[1], e[2]
        finally:
            del e

def task(rule=None, optional=False):
    """Define a task cell attribute"""
    return trellis._build_descriptor(
        rule=rule, factory=TaskCell.from_attr, optional=optional
    )






















