from sqlalchemy.orm.attributes import get_attribute,set_attribute,ClassManager
from trellis import Cells, NO_VALUE, CellFactories, Cell, Performer
from new import instancemethod

class SAInstrument(ClassManager):
    """Adapter for SQLAlchemy to talk to Trellis components"""

    def install_descriptor(self, key, inst):
        if key not in CellFactories(self.class_):
            setattr(self.class_, key, inst)

    def uninstall_descriptor(self, key):
        if key not in CellFactories(self.class_):
            delattr(self.class_, key)

    def install_state(self, instance, state):
        cells = Cells(instance)
        if not cells:
            cls = instance.__class__
            factories = CellFactories(cls)
            getter = instancemethod(get_attribute, instance)
            attrs = []
            for attr in self:
                if attr not in factories:
                    continue
                attrs.append(attr)
                cells[attr] = Cell(
                    instancemethod(getter, attr),
                    factories[attr].im_self.initial_value(instance) # XXX
                )
            def setter():
                for attr in attrs:
                    if cells[attr].was_set:
                        set_attribute(instance, attr, cells[attr].value)
            instance._observer = Performer(setter)
        super(SAInstrument, self).install_state(instance, state)
    

