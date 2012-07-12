from thread import get_ident
from weakref import ref
from peak.util import addons, decorators
import sys, UserDict, UserList, sets, stm, types, new, weakref
from peak.util.extremes import Max
from peak.util.symbols import Symbol, NOT_GIVEN

__all__ = [
    'Cell', 'Constant', 'make', 'todo', 'todos', 'modifier',
    'Component', 'repeat', 'poll', 'InputConflict',
    'Dict', 'List', 'Set', 'mark_dirty', 'ctrl', 'ConstantMixin', 'Sensor',
    'AbstractConnector', 'Connector',  'Effector', 'init_attrs',
    'attr', 'attrs', 'compute', 'maintain', 'perform', 'Performer', 'Pipe',
]

NO_VALUE = Symbol('NO_VALUE', __name__)
_sentinel = NO_VALUE


class InputConflict(Exception):
    """Attempt to set a cell to two different values during the same pulse"""


def init_attrs(self, **kw):
    """Initialize attributes from keyword arguments"""
    if kw:
        cls = type(self)
        for k, v in kw.iteritems():
            if not hasattr(cls, k):
                raise TypeError("%s() has no keyword argument %r"
                    % (cls.__name__, k)
                )
            setattr(self, k, v)

def named_lambda(func, name):
    if getattr(func,'__name__',None) == '<lambda>':
        try: func.__name__ = name
        except TypeError: pass  # Python 2.3 doesn't let you set __name__
    return func


try:
    set = set
except NameError:
    set = sets.Set
    frozenset = sets.ImmutableSet
    set_like = sets.BaseSet
    dictlike = dict, sets.BaseSet
else:
    set_like = set, frozenset, sets.BaseSet
    dictlike = (dict,) + set_like


class AbstractCell(object):
    """Base class for cells"""
    __slots__ = ()

    rule = value = _value = _needs_init = None
    writer = connector = None
    was_set = False
    _uninit_repr = ' [uninitialized]'

    def get_value(self):
        """Get the value of this cell"""
        return self.value

    def __repr__(self):
        rule = reset = ni = ''
        if getattr(self, 'rule', None) is not None:
            rule = repr(self.rule)+', '
        if self._needs_init:
            ni = self._uninit_repr
        if getattr(self, '_reset', _sentinel) is not _sentinel:
            reset =', discrete['+repr(self._reset)+']'
        return '%s(%s%r%s%s)'% (
            self.__class__.__name__, rule, self._value, ni, reset
        )





class _ReadValue(stm.AbstractSubject, AbstractCell):
    """Base class for readable cells"""

    __slots__ = '_value', 'next_listener', '_set_by', '_reset', # XXX 'manager'

    def __init__(self, value=None, discrete=False):
        self._value = value
        self._set_by = _sentinel
        stm.AbstractSubject.__init__(self)
        self._reset = (_sentinel, value)[bool(discrete)]

    def get_value(self):
        if ctrl.active:
            # if atomic, make sure we're locked and consistent
            used(self)
        return self._value

    value = property(get_value)

    def _finish(self):
        if self._set_by is not _sentinel:
            change_attr(self, '_set_by', _sentinel)
        if self._reset is not _sentinel and self._value != self._reset:
            change_attr(self, '_value', self._reset)
            changed(self)

    decorators.decorate(property)
    def was_set(self):
        """True if value was set during this recalc"""
        if ctrl.current_listener is None:
            raise RuntimeError("was_set can only be accessed by a rule")
        used(self)
        who = self._set_by
        return who is not _sentinel and who is not self







class Value(_ReadValue):
    """A read-write value with optional discrete mode"""

    __slots__ = ('__weakref__')

    def set_value(self, value):
        if not ctrl.active:
            return atomically(self.set_value, value)

        lock(self)
        if self._set_by is _sentinel:
            change_attr(self, '_set_by', ctrl.current_listener)
            on_commit(self._finish)

        if value is self._value:
            return  # no change, no foul...

        if value!=self._value:
            if self._set_by is not ctrl.current_listener:
                # already set by someone else
                raise InputConflict(self._value, value) #self._set_by) #, value, ctrl.current_listener) # XXX
            changed(self)

        change_attr(self, '_value', value)

    value = property(_ReadValue.get_value.im_func, set_value)


def install_controller(controller):
    global ctrl
    stm.ctrl = ctrl = controller
    for name in [
        'on_commit', 'on_undo', 'atomically', 'manage', 'savepoint',
        'rollback_to', 'schedule', 'cancel', 'lock', 'used', 'changed',
        'initialize', 'change_attr',
    ]:
        globals()[name] = getattr(ctrl, name)
        if name not in __all__: __all__.append(name)

install_controller(stm.LocalController())

class ReadOnlyCell(_ReadValue, stm.AbstractListener):
    """A cell with a rule"""
    __slots__ = 'rule', '_needs_init', 'next_subject', '__weakref__', 'layer'

    def __init__(self, rule, value=None, discrete=False):
        super(ReadOnlyCell, self).__init__(value, discrete)
        stm.AbstractListener.__init__(self)
        self._needs_init = True
        self.rule = rule
        self.layer = 0

    def get_value(self):
        if self._needs_init:
            if not ctrl.active:
                # initialization must be atomic
                atomically(schedule, self)
                return self._value
            else:
                cancel(self); initialize(self)
        if ctrl.current_listener is not None:
            used(self)
        return self._value

    value = property(get_value)

    def run(self):
        if self._needs_init:
            change_attr(self, '_needs_init', False)
            change_attr(self, '_set_by', self)
            change_attr(self, '_value', self.rule())
            on_commit(self._finish)
        else:
            value = self.rule()
            if value!=self._value:
                if self._set_by is _sentinel:
                    change_attr(self, '_set_by', self)
                    on_commit(self._finish)
                change_attr(self, '_value', value)
                changed(self)
        if not ctrl.reads: on_commit(self._check_const)

    def _check_const(self):
        if self.next_subject is None and (
            self._reset is _sentinel or self._value==self._reset
        ):
            change_attr(self, '_set_by', _sentinel)
            change_attr(self, 'rule', None)
            change_attr(self, 'next_listener', None)
            change_attr(self, '__class__', self._const_class())

    def _const_class(self):
        return ConstantRule


class ConstantMixin(AbstractCell):
    """A read-only abstract cell"""

    __slots__ = ()

    def __setattr__(self, name, value):
        """Constants can't be changed"""
        if name == '__class__':
            object.__setattr__(self, name, value)
        else:
            raise AttributeError("Constants can't be changed")

    def __repr__(self):
        return "Constant(%r)" % (self.value,)

class Constant(ConstantMixin):
    """A pure read-only value"""

    __slots__ = 'value'

    def __init__(self, value):
        Constant.value.__set__(self, value)

    decorators.decorate(classmethod)
    def from_attr(cls, rule, value, discrete):
        return cls(value)


class ConstantRule(ConstantMixin, ReadOnlyCell):
    """A read-only cell that no longer depends on anything else"""

    __slots__ = ()

    value = ReadOnlyCell._value

    def dirty(self):
        """Constants don't need recalculation"""
        return False

    def run(self):
        """Constants don't run"""



class Performer(stm.AbstractListener, AbstractCell):
    """Rule that performs non-undoable actions"""

    __slots__ = 'run', 'next_subject', '__weakref__'

    layer = Max

    def __init__(self, rule):
        self.run = rule
        super(Performer, self).__init__()
        atomically(schedule, self)

    decorators.decorate(classmethod)
    def from_attr(cls, rule, value, discrete):
        return cls(rule)

Performer.rule = Performer.run    # alias the attribute for inspection








def modifier(func):
    """Mark a function as performing modifications to Trellis data

    The wrapped function will always run atomically, and if called from inside
    a rule, reads performed in the function will not become dependencies of the
    caller.
    """
    def wrap(__func, __module):
        """
        if not __module.ctrl.active:
            return __module.atomically(__func, $args)
        elif __module.ctrl.current_listener is None:
            return __func($args)
        else:
            # Prevent any reads from counting against the current rule
            old_reads, __module.ctrl.reads = __module.ctrl.reads, {}
            try:
                return __func($args)
            finally:
                __module.ctrl.reads = old_reads
        """
    return decorators.template_function(wrap)(func, sys.modules[__name__])



















set_next_listener = ReadOnlyCell.next_listener.__set__
get_next_listener = ReadOnlyCell.next_listener.__get__

class SensorBase(ReadOnlyCell):
    """Base for cells that connect to non-Trellis code"""

    __slots__ = ()

    def __init__(self, rule, value=None, discrete=False):
        if isinstance(rule, AbstractConnector):
            self.connector = rule
            rule = rule.read
        else:
            self.connector = None
        self.listening = NOT_GIVEN
        set_next_listener(self, None)
        super(SensorBase, self).__init__(rule, value, discrete)

    def _set_listener(self, listener):
        was_seen = get_next_listener(self) is not None
        set_next_listener(self, listener)
        if was_seen != (listener is not None) and self.connector is not None:
            atomically(on_commit, schedule, self.update_connection)

    next_listener = property(get_next_listener, _set_listener)

    _set_value = Value.set_value.im_func

    decorators.decorate(modifier)
    def receive(self, value):
        if not ctrl.active:
            return atomically(self.receive, value)
        lock(self)
        self._set_value(value)
        change_attr(self, '_set_by', self)

    def _check_const(self): pass    # we can never become Constant




    def update_connection():
        old_listener, ctrl.current_listener = ctrl.current_listener, None
        try:
            self = old_listener.im_self
            descr = type(self).listening
            listening = descr.__get__(self)
            if self.next_listener is not None:
                if listening is NOT_GIVEN:
                    descr.__set__(self, self.connector.connect(self))
            elif listening is not NOT_GIVEN:
                self.connector.disconnect(self, listening)
                descr.__set__(self, NOT_GIVEN)
        finally:
            ctrl.current_listener = old_listener

    update_connection.run = update_connection
    update_connection.next_subject = update_connection.next_listener = None
    update_connection.layer = -1

class Sensor(SensorBase):
    """A cell that can receive value callbacks from the outside world"""
    __slots__ = 'connector', 'listening'

class AbstractConnector(object):
    """Base class for rules that connect to the outside world"""
    __slots__ = ()

    def read(self):
        """Return a value from the outside source"""
        # Just use the current/last received value by default
        return ctrl.current_listener._value

    def connect(self, sensor):
        """Connect the sensor to the outside world, returning disconnect key

        This method must arrange callbacks to ``sensor.receive(value)``, and
        return an object suitable for use by ``disconnect()``."""

    def disconnect(self, sensor, key):
        """Disconnect the key returned by ``connect()``"""

class Connector(AbstractConnector):
    """Trivial connector, wrapping three functions"""

    __slots__ = "read", "connect", "disconnect"

    def __init__(self, connect, disconnect, read=None):
        if read is None:
            read = noop
        self.read = read
        self.connect = connect
        self.disconnect = disconnect


def noop():
    """A rule that leaves its current/initial value unchanged"""
    return ctrl.current_listener._value



class LazyConnector(AbstractConnector):
    """Dummy connector object used for lazy cells"""

    decorators.decorate(staticmethod)
    def connect(sensor):
        pass

    decorators.decorate(staticmethod)
    def disconnect(sensor, key):
        link = sensor.next_subject
        if link is not None: change_attr(sensor, '_needs_init', True)
        while link is not None:
            nxt = link.next_subject   # avoid unlinks breaking iteration
            on_undo(stm.Link, link.subject, sensor)
            link.unlink()
            link = nxt






class LazyCell(Sensor):
    """A ReadOnlyCell that is only recalculated when it has listeners"""

    __slots__ = ()
    _uninit_repr = ' [inactive]'

    def __init__(self, rule, value=None, discrete=False):
        super(LazyCell, self).__init__(rule, value, discrete)
        #if self.connector is not None: raise XXX
        self.connector = LazyConnector

    _check_const = ReadOnlyCell._check_const

    def run(self):
        run = super(LazyCell, self).run
        if not ctrl.readonly:
            ctrl.with_readonly(run)
        else: run()
        if self.listening is NOT_GIVEN:  # may need to disconnect...
            self.listening = None; on_commit(schedule, self.update_connection)

    def _const_class(self):
        return LazyConstant

    def get_value(self):
        if ctrl.current_listener is self:
            raise RuntimeError("@compute rules cannot use their own value")
        return super(LazyCell, self).get_value()

    value = property(get_value)


class LazyConstant(ConstantRule, LazyCell):
    """LazyCell version of a constant"""
    __slots__ = ()






class Cell(ReadOnlyCell, Value):
    """Spreadsheet-like cell with automatic updating"""

    __slots__ = ()

    def __new__(cls, rule=None, value=_sentinel, discrete=False):
        v = [value,None][value is _sentinel]
        if cls is Cell:
            if isinstance(rule, AbstractConnector) and cls is Cell:
                if value is _sentinel:
                    return Sensor(rule, v, discrete)
                return Effector(rule, value, discrete)
            elif value is _sentinel and rule is not None:
                return ReadOnlyCell(rule, None, discrete)
            elif rule is None:
                return Value(v, discrete)
        return ReadOnlyCell.__new__(cls, rule, value, discrete)

    def _check_const(self):
        pass    # we can never become Constant

    def get_value(self):
        if self._needs_init:
            if not ctrl.active:
                atomically(schedule, self)  # initialization must be atomic
                return self._value
            if self._set_by is _sentinel:
                # No value set yet, so we have to run() first
                cancel(self); initialize(self)
        if ctrl.current_listener is not None:
            used(self)
        return self._value

    def set_value(self, value):
        if not ctrl.active:
            return atomically(self.set_value, value)
        super(Cell, self).set_value(value)
        if self._needs_init:
            schedule(self)


    value = property(get_value, set_value)

    def dirty(self):
        # If we've been manually set, don't reschedule
        who = self._set_by
        return who is _sentinel or who is self

    def run(self):
        if self.dirty():
            # Nominal case: the value hasn't been set in this txn, or was only
            # set by the rule itself.
            super(Cell, self).run()
        elif self._needs_init:
            # Initialization case: value was set before reading, so we ignore
            # the return value of the rule and leave our current value as-is,
            # but of course now we will notice any future changes
            change_attr(self, '_needs_init', False)
            self.rule()
        else:
            # It should be impossible to get here unless you run the cell
            # manually.  Don't do that.  :)
            raise AssertionError("This should never happen!")


class Effector(SensorBase, Cell):
    """Writable Sensor"""

    __slots__ = 'connector', 'listening'













class _Defaulting(addons.Registry):
    def __init__(self, subject):
        self.defaults = {}
        return super(_Defaulting, self).__init__(subject)

    def created_for(self, cls):
        for k,v in self.defaults.items():
            self.setdefault(k, v)
        return super(_Defaulting, self).created_for(cls)

class CellFactories(_Defaulting):
    """Registry for cell factories"""

class IsOptional(_Defaulting):
    """Registry for flagging that an attribute need not be activated"""

class Cells(addons.AddOn):
    __slots__ = ()
    addon_key = classmethod(lambda cls: '__cells__')
    def __new__(cls, subject): return {}





















class Component(decorators.classy):
    """Base class for objects with Cell attributes"""

    __slots__ = ()

    decorators.decorate(classmethod, modifier)
    def __class_call__(cls, *args, **kw):
        optional = IsOptional(cls)  # ensure initialization beforehand
        rv = super(Component, cls).__class_call__(*args, **kw)
        if isinstance(rv, cls):
            cells = Cells(rv)
            for k, v in optional.iteritems():
                if not v and k not in cells:
                    c = cells.setdefault(k, CellFactories(cls)[k](cls, rv, k))
                    c.value     # XXX
        return rv

    __init__ = init_attrs

    decorators.decorate(staticmethod)
    def __sa_instrumentation_manager__(cls):
        from peak.events.sa_support import SAInstrument
        return SAInstrument(cls)

    def __class_init__(cls, name, bases, cdict, supr):
        supr()(cls, name, bases, cdict, supr)
        try: Component
        except NameError: return
        optional = IsOptional(cls)
        factories = CellFactories(cls)
        for k,descr in cdict.items():
            if isinstance(descr, CellAttribute):
                if descr.__name__ is None: descr.__name__ = k
                optional[k] = descr.optional
                factories[k] = descr.make_cell
            elif k in optional:
                # Don't create a cell for overridden non-CellProperty attribute
                optional[k] = True



def repeat():
    """Schedule the current rule to be run again, repeatedly"""
    if ctrl.current_listener is not None:
        on_commit(schedule, ctrl.current_listener)
    else:
        raise RuntimeError("repeat() must be called from a rule")

def poll():
    """Recalculate this rule the next time *any* other cell is set"""
    listener = ctrl.current_listener
    if listener is None or not hasattr(listener, '_needs_init'):
        raise RuntimeError("poll() must be called from a rule")
    else:
        return ctrl.pulse.value

def mark_dirty():
    """Force the current rule's return value to be treated as if it changed"""
    assert ctrl.current_listener is not None, "dirty() must be called from a rule"
    changed(ctrl.current_listener)


def bind(rule, ob, typ=None):
    if hasattr(rule, '__get__'):
        return rule.__get__(ob, typ)
    return rule
    















class CellAttribute(object):
    """Self-contained cell descriptor"""

    value = NO_VALUE
    rule = connect = disconnect = None
    make = None
    factory = Cell
    discrete = False
    optional = False
    __name__ = None
    __init__ = init_attrs

    def initial_value(self, ob):
        if self.value is NO_VALUE:
            if self.make is not None:
                return build_value(self.make, ob, self.__name__)
            elif self.rule is not None:
                return None
        return self.value

    def make_cell(self, typ, ob, name):
        rule = bind(self.rule, ob, typ)
        if self.connect is not None or self.disconnect is not None:
            connect = bind(self.connect, ob, typ)
            disconnect = bind(self.disconnect, ob, typ)
            missing = 'disconnect'
            if connect is None:
                missing='connect'
            if connect is None or disconnect is None:
                raise TypeError("%r is missing a .%sor" % (self,missing))
            rule = Connector(connect, disconnect, rule)
        return self.factory(rule, self.initial_value(ob), self.discrete)

    def connector(self, func=None):
        """Decorate a method as providing a connect function for this cell"""
        return self._hook_method('connect', func)

    def disconnector(self, func=None):
        """Decorate a method as providing a disconnect function for this cell"""
        return self._hook_method('disconnect', func)

    def __get__(self, ob, typ=None):
        if ob is None:
            return self
        try:
            cells = ob.__cells__
        except AttributeError:
            cells = Cells(ob)
        try:
            cell = cells[self.__name__]
        except KeyError:
            name = self.__name__
            cell = cells.setdefault(name, self.make_cell(typ, ob, name))
        return cell.value

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__name__)

    def __set__(self, ob, value):
        try:
            cells = ob.__cells__
        except AttributeError:
            cells = Cells(ob)

        if isinstance(value, AbstractCell):
            name = self.__name__
            if name in cells and isinstance(cells[name], ConstantMixin):
                raise AttributeError("Can't change a constant")
            cells[name] = value
        else:
            try:
                cell = cells[self.__name__]
            except KeyError:
                name = self.__name__
                typ = type(ob)
                cell = self.make_cell(typ, ob, name)
                if not hasattr(cell, 'set_value'):
                    return cells.setdefault(name, Constant(value))
                cell = cells.setdefault(name, cell)
            cell.value = value


    decorators.decorate(classmethod)
    def mkattr(cls, initially=NO_VALUE, resetting_to=NO_VALUE, **kw):
        if initially is not NO_VALUE and resetting_to is not NO_VALUE:
            raise TypeError("Can't specify both 'initially' and 'resetting_to'")
        value = initially
        discrete = False
        if resetting_to is not NO_VALUE:
            value = resetting_to
            discrete = True
        if value is not NO_VALUE and kw.get('make') is not None:
            raise TypeError("Can't specify both a value and 'make'")

        return cls(value=value, discrete=discrete, **kw)


    def can_connect(self):
        """Can this attribute have ``.connect`` and ``.disconnect`` methods?

        By default, only @compute and @maintain rules can.  Subclasses should
        override this if they override ``factory()`` and still want to support
        connect/disconnect methods.
        """
        if self.factory is LazyCell:
            self.factory = Sensor   # XXX kludge!
        else:
            return self.factory is Cell or self.factory is Sensor
        return True














    def _hook_method(self, methodname, func=None, frame=None):
        if not self.can_connect():
            raise TypeError("%r cannot have a .%sor" % (self, methodname))

        if isinstance(self.rule, AbstractConnector):
            raise TypeError("The rule for %r is itself a Connector" % (self,))

        if getattr(self, methodname) is not None:
            raise TypeError("%r already has a .%sor" % (self, methodname))

        if func is not None:
            setattr(self, methodname, func)
            return self

        frame = frame or sys._getframe(2)
        def callback(frame, name, func, locals):
            setattr(self, methodname, func)
            if name==self.__name__ and locals.get(name) is self:
                return self
            return func

        return decorators.decorate_assignment(callback, frame=frame)
        


















def attr(initially=NO_VALUE, resetting_to=NO_VALUE):
    return CellAttribute.mkattr(initially, resetting_to)

def compute(rule=None, resetting_to=NO_VALUE):
    return _build_descriptor(
        rule=rule, resetting_to=resetting_to, factory=LazyCell, optional=True
    )

def maintain(rule=None, make=None, initially=NO_VALUE, resetting_to=NO_VALUE, optional=False):
    return _build_descriptor(
        rule=rule, initially=initially, resetting_to=resetting_to, make=make,
        optional=optional
    )

def perform(rule=None, optional=False):
    return _build_descriptor(
        rule=rule, factory=Performer.from_attr, optional=optional
    )

def compute_attrs(**attrs):
    """Define multiple rule-cell attributes"""
    _make_multi(sys._getframe(1), attrs, factory=LazyCell, optional=True)
compute.attrs = compute_attrs

def maintain_attrs(**attrs):
    """Define multiple rule-cell attributes"""
    _make_multi(sys._getframe(1), attrs)
maintain.attrs = maintain_attrs

def attrs(**attrs):
    """Define multiple value-cell attributes"""
    _make_multi(sys._getframe(1), attrs, arg='initially')


def attrs_resetting_to(**attrs):
    """Define multiple receiver-cell attributes"""
    _make_multi(sys._getframe(1), attrs, arg='resetting_to')
attrs.resetting_to = attrs_resetting_to



def _make_multi(frame, kw, wrap=CellAttribute.mkattr, arg='rule', **opts):
    for k, v in kw.items():
        if k in frame.f_locals:
            raise TypeError("%s is already defined in this class" % (k,))
        opts[arg] = named_lambda(v, k)
        frame.f_locals[k]= wrap(__name__=k, **opts)

def _build_descriptor(
    rule=None, __frame=None, __name=None, __proptype = CellAttribute.mkattr,
    __ruleattr='rule', **kw
):
    frame = __frame or sys._getframe(2)
    name  = __name
    if isinstance(rule, types.FunctionType): # only pick up name if a function
        if frame.f_locals.get(rule.__name__) is rule:   # and locally-defined!
            name = name or rule.__name__

    def callback(frame, name, rule, locals):
        kw[__ruleattr] = named_lambda(rule, name)
        return __proptype(__name__=name, **kw)

    if name:
        # Have everything we need, just go for it
        return callback(frame, name, rule, None)
    elif rule is not None:
        # We know everything but the name, so return the rule as-is and trap
        # the assignment...
        decorators.decorate_assignment(callback, frame=frame)
        return rule
    else:
        # We're being used as a decorator, so just decorate.
        return decorators.decorate_assignment(callback, frame=frame)

def todos(**attrs):
    """Define multiple todo-cell attributes"""
    _make_multi(sys._getframe(1), attrs, TodoProperty.mkattr)

def todo(rule=None):
    """Define an attribute that can send "messages to the future" """
    return _build_descriptor(rule=rule, __proptype = TodoProperty.mkattr)

class TodoProperty(CellAttribute):
    """Property representing a ``todo`` attribute"""

    decorators.decorate(property)
    def future(self):
        """Get a read-only property for the "future" of this attribute"""
        name = self.__name__
        def get(ob):
            try: cells = ob.__cells__
            except AttributeError: cells = Cells(ob)
            try:
                cell = cells[name]
            except KeyError:
                typ = type(ob)
                cell = cells.setdefault(name, self.make_cell(typ, ob, name))
            return cell.get_future()
        return property(get, doc="The future value of the %r attribute" % name)

    def factory(self, rule, value, discrete):
        return TodoValue(rule)

def build_value(make, ob, name):
    if hasattr(make, '__get__'):
        make = make.__get__(ob, type(ob))
    return make()

def make(rule=None, writable=False, optional=True):
    """Create a Constant or Value, initialized from `rule()`"""
    return _build_descriptor(
        rule, optional=optional, __ruleattr='make',
        factory=[Constant.from_attr, Cell][bool(writable)]
    )

def make_attrs(**attrs):
    """Define multiple make-constant attributes"""
    _make_multi(
        sys._getframe(1), attrs,
        factory=Constant.from_attr, arg='make', optional=True
    )
make.attrs = make_attrs

class TodoValue(Value):
    """Value that logs changes for mutable data structures"""

    __slots__ = 'rule', '_savepoint'

    def __new__(cls, rule):
        return Value.__new__(cls)

    def __init__(self, rule):
        self.rule = rule
        self._savepoint = None
        Value.__init__(self, rule(), True)

    def set_value(self, value):
        if not ctrl.active:
            atomically(self.set_value, value)
        lock(self)
        if self._savepoint is None:
            change_attr(self, '_savepoint', savepoint())
        else:
            on_undo(rollback_to, self._savepoint)
        super(TodoValue, self).set_value(value)

    value = property(Value.get_value.im_func, set_value)

    def get_future(self):
        """Get the 'future' value"""
        if not ctrl.active:
            raise RuntimeError("future can only be accessed from a @modifier")
        lock(self)
        if self._savepoint is None:
            self.value = self.rule()
            changed(self)
        else:
            on_undo(rollback_to, self._savepoint)
        return self._value

    def _finish(self):
        change_attr(self, '_savepoint', None)
        super(TodoValue, self)._finish()

class Pipe(Component):
    """Allow one or more writers to send data to zero or more readers"""

    output = todo(list)
    input  = output.future

    decorators.decorate(modifier)
    def append(self, value):
        self.input.append(value)

    decorators.decorate(modifier)
    def extend(self, sequence):
        self.input.extend(sequence)

    def __iter__(self):
        return iter(self.output)

    def __contains__(self, value):
        return value in self.output

    def __len__(self):
        return len(self.output)

    def __repr__(self):
        return repr(self.output)
















class WeakDefaultDict(weakref.WeakValueDictionary):

    def __init__(self, missing):
        weakref.WeakValueDictionary.__init__(self)
        self.__missing__ = missing

    def __getitem__(self, key):
        try:
            return weakref.WeakValueDictionary.__getitem__(self, key)
        except KeyError:
            value = self.__missing__(key)
            self[key] = value
            return value

class CacheAttr(CellAttribute):
    optional = True
    def can_connect(self): return True
    def factory(self, rule, value, discrete):
        #if (isinstance(rule, Connector)
        #    and not isinstance(self.rule, AbstractConnector)
        #):
        conn, disc, rule = rule.connect, rule.disconnect, rule.read
        #else:
        #    conn = disc = None
        def make_cell(key):
            #if not isinstance(rule, AbstractConnector):
            r = new.instancemethod(rule, key, type(key))
            #if conn is None:
            #    return LazyCell(r, value, discrete)
            return Sensor(
                Connector(lambda s: conn(key), lambda s,m: disc(key), r),
                value, discrete
            )
        return Constant(WeakDefaultDict(make_cell))

def cellcache(rule=None, make=None, initially=NO_VALUE, resetting_to=NO_VALUE):
    return _build_descriptor(
        rule=rule, initially=initially, resetting_to=resetting_to, make=make,
        __proptype = CacheAttr.mkattr
    )
    
class Dict(UserDict.IterableUserDict, Component):
    """Dictionary-like object that recalculates observers when it's changed

    The ``added``, ``changed``, and ``deleted`` attributes are dictionaries
    showing the current added/changed/deleted contents.  Note that ``changed``
    may include items that were set as of this recalc, but in fact have the
    same value as they had in the previous recalc, as no value comparisons are
    done!

    You may observe these attributes directly, but any rule that reads the
    dictionary in any way (e.g. gets items, iterates, checks length, etc.)
    will be recalculated if the dictionary is changed in any way.

    Note that this operations like pop(), popitem(), and setdefault() that both
    read and write in the same operation are NOT supported, since reading must
    always happen in the present, whereas writing is done to the future version
    of the dictionary.
    """
    added = todo(dict)
    deleted = todo(dict)
    changed = todo(dict)

    to_add = added.future
    to_change = changed.future
    to_delete = deleted.future

    def __init__(self, other=(), **kw):
        Component.__init__(self)
        if other: self.data.update(other)
        if kw:    self.data.update(kw)

    def copy(self):
        return self.__class__(self.data)

    def get(self, key, failobj=None):
        return self.data.get(key, failobj)

    def __hash__(self):
        raise TypeError


    maintain(make=dict)
    def data(self):
        data = self.data
        if self.deleted or self.changed:
            old = [(k,data[k]) for k in self.deleted if k in data]
            old += [(k,data[k]) for k in self.changed if k in data]
            on_undo(data.update, dict(old))
        pop = data.pop
        if self.deleted:
            mark_dirty()
            for key in self.deleted:
                pop(key, None)
        if self.added:
            for key in self.added: on_undo(pop, key, None)
            mark_dirty(); data.update(self.added)
        if self.changed:
            mark_dirty(); data.update(self.changed)
        return data

    decorators.decorate(modifier)
    def __setitem__(self, key, item):
        if key in self.to_delete:
            del self.to_delete[key]
        if key in self.data:
            self.to_change[key] = item
        else:
            self.to_add[key] = item

    decorators.decorate(modifier)
    def __delitem__(self, key):
        if key in self.to_add:
            del self.to_add[key]
        elif key in self.data and key not in self.to_delete:
            self.to_delete[key] = self.data[key]
            if key in self.to_change:
                del self.to_change[key]
        else:
            raise KeyError, key



    decorators.decorate(modifier)
    def clear(self):
        self.to_add.clear()
        self.to_change.clear()
        self.to_delete.update(self.data)

    decorators.decorate(modifier)
    def update(self, d=(), **kw):
        if d:
            if kw:
                d = dict(d);  d.update(kw)
            elif not hasattr(d, 'iteritems'):
                d = dict(d)
        else:
            d = kw
        to_change = self.to_change
        to_add = self.to_add
        to_delete = self.to_delete
        data = self.data
        for k, v in d.iteritems():
            if k in to_delete:
                del to_delete[k]
            if k in data:
                to_change[k] = d[k]
            else:
                to_add[k] = d[k]

    def setdefault(self, key, failobj=None):
        """setdefault() is disallowed because it 'reads the future'"""
        raise InputConflict("Can't read and write in the same operation")

    def pop(self, key, *args):
        """The pop() method is disallowed because it 'reads the future'"""
        raise InputConflict("Can't read and write in the same operation")

    def popitem(self):
        """The popitem() method is disallowed because it 'reads the future'"""
        raise InputConflict("Can't read and write in the same operation")



class List(UserList.UserList, Component):
    """List-like object that recalculates observers when it's changed

    The ``changed`` attribute is True whenever the list has changed as of the
    current recalculation, and any rule that reads the list in any way (e.g.
    gets items, iterates, checks length, etc.) will be recalculated if the
    list is changed in any way.

    Note that this type is not efficient for large lists, as a copy-on-write
    strategy is used in each recalcultion that changes the list.  If what you
    really want is e.g. a sorted read-only view on a set, don't use this.
    """

    updated = todo(lambda self: self.data[:])
    future  = updated.future
    changed = todo(bool)

    def __init__(self, other=(), **kw):
        Component.__init__(self, **kw)
        self.data[:] = other

    maintain(make=list)
    def data(self):
        if self.changed:
            mark_dirty()
            return self.updated
        return self.data

    decorators.decorate(modifier)
    def __setitem__(self, i, item):
        self.changed = True
        self.future[i] = item

    decorators.decorate(modifier)
    def __delitem__(self, i):
        self.changed = True
        del self.future[i]




    decorators.decorate(modifier)
    def __setslice__(self, i, j, other):
        self.changed = True
        self.future[i:j] = other

    decorators.decorate(modifier)
    def __delslice__(self, i, j):
        self.changed = True
        del self.future[i:j]

    decorators.decorate(modifier)
    def __iadd__(self, other):
        self.changed = True
        self.future.extend(other)
        return self

    decorators.decorate(modifier)
    def append(self, item):
        self.changed = True
        self.future.append(item)

    decorators.decorate(modifier)
    def insert(self, i, item):
        self.changed = True
        self.future.insert(i, item)

    decorators.decorate(modifier)
    def extend(self, other):
        self.changed = True
        self.future.extend(other)

    decorators.decorate(modifier)
    def __imul__(self, n):
        self.changed = True
        self.future[:] = self.future * n
        return self





    decorators.decorate(modifier)
    def remove(self, item):
        self.changed = True
        self.future.remove(item)

    decorators.decorate(modifier)
    def reverse(self):
        self.changed = True
        self.future.reverse()

    decorators.decorate(modifier)
    def sort(self, *args, **kw):
        self.changed = True
        self.future.sort(*args, **kw)

    def pop(self, i=-1):
        """The pop() method isn't supported, because it 'reads the future'"""
        raise InputConflict(
            "Can't read and write in the same operation"
        )

    def __hash__(self):
        raise TypeError


















class Set(sets.Set, Component):
    """Mutable set that recalculates observers when it's changed

    The ``added`` and ``removed`` attributes can be watched for changes, but
    any rule that simply uses the set (e.g. iterates over it, checks for
    membership or size, etc.) will be recalculated if the set is changed.
    """
    _added = todo(set)
    _removed = todo(set)
    added, removed = _added, _removed
    to_add = _added.future
    to_remove = _removed.future

    def __init__(self, iterable=None, **kw):
        """Construct a set from an optional iterable."""
        Component.__init__(self, **kw)
        if iterable is not None:
            # we can update self._data in place, since no-one has seen it yet
            sets.Set._update(self, iterable)

    maintain(make=dict)
    def _data(self):
        """The dictionary containing the set data."""
        data = self._data
        pop = data.pop
        if self.removed:
            mark_dirty()
            for item in self.removed: pop(item, None)
            on_undo(data.update, dict.fromkeys(self.removed, True))
        if self.added:
            mark_dirty()
            data.update(dict.fromkeys(self.added, True))
            for item in self.added: on_undo(pop, item, None)
        return data

    def __setstate__(self, data):
        self.__init__(data[0])




    def _binary_sanity_check(self, other):
        # Check that the other argument to a binary operation is also
        # a set, raising a TypeError otherwise.
        if not isinstance(other, set_like):
            raise TypeError, "Binary operation only permitted between sets"

    def pop(self):
        """The pop() method isn't supported, because it 'reads the future'"""
        raise InputConflict(
            "Can't read and write in the same operation"
        )

    decorators.decorate(modifier)
    def _update(self, iterable):
        to_remove = self.to_remove
        add = self.to_add.add
        for item in iterable:
            if item in to_remove:
                to_remove.remove(item)
            else:
                add(item)

    decorators.decorate(modifier)
    def add(self, item):
        """Add an element to a set (no-op if already present)"""
        if item in self.to_remove:
            self.to_remove.remove(item)
        elif item not in self._data:
            self.to_add.add(item)

    decorators.decorate(modifier)
    def remove(self, item):
        """Remove an element from a set (KeyError if not present)"""
        if item in self.to_add:
            self.to_add.remove(item)
        elif item in self._data and item not in self.to_remove:
            self.to_remove.add(item)
        else:
            raise KeyError(item)


    decorators.decorate(modifier)
    def clear(self):
        """Remove all elements from this set."""
        self.to_remove.update(self)
        self.to_add.clear()

    def __ior__(self, other):
        """Update a set with the union of itself and another."""
        self._binary_sanity_check(other)
        self._update(other)
        return self

    def __iand__(self, other):
        """Update a set with the intersection of itself and another."""
        self._binary_sanity_check(other)
        self.intersection_update(other)
        return self

    decorators.decorate(modifier)
    def difference_update(self, other):
        """Remove all elements of another set from this set."""
        data = self._data
        to_add, to_remove = self.to_add, self.to_remove
        for item in other:
            if item in to_add: to_add.remove(item)
            elif item in data: to_remove.add(item)

    decorators.decorate(modifier)
    def intersection_update(self, other):
        """Update a set with the intersection of itself and another."""
        to_remove = self.to_remove
        to_add = self.to_add
        self.to_add.intersection_update(other)
        other = to_dict_or_set(other)
        for item in self._data:
            if item not in other:
                to_remove.add(item)
        return self



    decorators.decorate(modifier)
    def symmetric_difference_update(self, other):
        """Update a set with the symmetric difference of itself and another."""
        data = self._data
        to_add = self.to_add
        to_remove = self.to_remove
        for elt in to_dict_or_set(other):
            if elt in to_add:
                to_add.remove(elt)      # Got it; get rid of it
            elif elt in to_remove:
                to_remove.remove(elt)   # Don't got it; add it
            elif elt in data:
                to_remove.add(elt)      # Got it; get rid of it
            else:
                to_add.add(elt)         # Don't got it; add it

def to_dict_or_set(ob):
    """Return the most basic set or dict-like object for ob
    If ob is a sets.BaseSet, return its ._data; if it's something we can tell
    is dictlike, return it as-is.  Otherwise, make a dict using .fromkeys()
    """
    if isinstance(ob, sets.BaseSet):
        return ob._data
    elif not isinstance(ob, dictlike):
        return dict.fromkeys(ob)
    return ob















