from copy import deepcopy

from flask_ember.dsl.class_mutator_base import ClassMutatorBase
from flask_ember.resource.configuration.resource_configurator_base import \
    ResourceConfiguratorBase
from flask_ember.util.meta import (get_class_attributes,
                                   get_inherited_attributes)
from .resource_descriptor import ResourceDescriptor
from .resource_property_base import ResourcePropertyBase


class ResourceMeta(type):
    """ The metaclass of a resource. It is responsible for collecting and
    managing properties and applying configurators and mutators to resource
    classes.

    :param cls: The generated class.
    :type cls: ResourceMeta
    :param name: The name of the generated class.
    :type name: str
    :param bases: The base classes of the generated class.
    :type bases: str
    :param attrs: The attributes of the generated class.
    :type attrs: dict
    """

    def __init__(cls, name, bases, attrs):
        print("\nGenerating %s\n" % name)
        # TODO this check is a dirty hack and should be improved
        if not hasattr(cls._ember, 'Resource'):
            # if this is the resource base class ignore instrumentation, this
            # works because when the resource base is generated, it is not set
            # in the ember object
            return

        ResourceMeta.instrument_resource(cls)
        super().__init__(name, bases, attrs)

    @staticmethod
    def instrument_resource(cls):
        """ Instruments the given resource class. Therefore a
        :class:`ResourceDescriptor` is registered at the class and can be
        accessed by the _configurator property. Further all properties are
        collected (from the resource class itself and the base classes) and
        registered at the descriptor. All registered class mutators and
        configurators are executed. Finally the resource is registered at
        the central :class:`FlaskEmber` instance.

        :param cls: The resource class that is to be instrumented.
        :type cls: ResourceMeta
        """
        descriptor = cls._descriptor = ResourceDescriptor(cls)

        # TODO if this is an abstract class really abort here?
        if descriptor.options.abstract:
            return

        cls._table = None
        cls._mapper = None

        ResourceMeta.collect_and_register_properties(cls)
        ResourceConfiguratorBase.apply_configurators(cls)
        ClassMutatorBase.apply_mutators(cls)

        cls._ember.register_resource(cls)

    @staticmethod
    def collect_and_register_properties(cls):
        """ Collects all properties from the resource class and its base
        classes and registers them at the resource's descriptor.

        :param cls: The resource class.
        :type cls: ResourceMeta
        """
        properties = ResourceMeta.collect_and_copy_properties(cls)
        for name, prop in properties:
            prop.register_at_resource(cls, name)

    @staticmethod
    def collect_and_copy_properties(cls):
        """ Collects all properties from the resource class and its base
        classes and returns them as list. All inherited properties are deep
        copied.

        :param cls: The resource class.
        :rtype: list
        """
        # TODO filter properties from base classes that are no resources and
        # thus are no instance from ResourceMeta
        property_order = lambda pair: pair[1]._creation_index
        inherited_properties = get_inherited_attributes(
            cls, ResourceMeta.is_property, order=property_order)
        base_properties = map(lambda prop: (prop[0], deepcopy(prop[1])),
                              inherited_properties)
        properties = get_class_attributes(cls, ResourceMeta.is_property,
                                          order=property_order)
        print(list(base_properties))
        print(properties)
        return list(base_properties) + properties

    @staticmethod
    def is_property(name, attribute):
        """ Returns whether the given attribute with the given name is a
        property.

        :param name: The name of the attribute.
        :type name: str
        :param attribute: The attribute.
        :rtype: bool
        """
        return isinstance(attribute, ResourcePropertyBase)
