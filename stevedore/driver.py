from .named import NamedExtensionManager


class DriverManager(NamedExtensionManager):
    """Load a single plugin with a given name from the namespace.

    :param namespace: The namespace for the entry points.
    :type namespace: str
    :param name: The name of the driver to load.
    :type name: str
    :param invoke_on_load: Boolean controlling whether to invoke the
        object returned by the entry point after the driver is loaded.
    :type invoke_on_load: bool
    :param invoke_args: Positional arguments to pass when invoking
        the object returned by the entry point. Only used if invoke_on_load
        is True.
    :type invoke_args: tuple
    :param invoke_kwds: Named arguments to pass when invoking
        the object returned by the entry point. Only used if invoke_on_load
        is True.
    :type invoke_kwds: dict
    """

    def __init__(self, namespace, name,
                 invoke_on_load=False, invoke_args=(), invoke_kwds={}):
        super(DriverManager, self).__init__(
            namespace=namespace,
            names=[name],
            invoke_on_load=invoke_on_load,
            invoke_args=invoke_args,
            invoke_kwds=invoke_kwds,
        )

    @classmethod
    def make_test_instance(cls, extension, namespace='TESTING',
                           propagate_map_exceptions=False):
        """Construct a test DriverManager

        Test instances are passed a list of extensions to work from rather
        than loading them from entry points.

        :param extension: Pre-configured Extension instance
        :type extension: :class:`~stevedore.extension.Extension`
        :param namespace: The namespace for the manager; used only for
            identification since the extensions are passed in.
        :type namespace: str
        :param propagate_map_exceptions: Boolean controlling whether exceptions
            are propagated up through the map call or whether they are logged
            and then ignored
        :type propagate_map_exceptions: bool
        :return: The manager instance, initialized for testing

        """

        o = super(DriverManager, cls).make_test_instance(
            [extension], namespace=namespace,
            propagate_map_exceptions=propagate_map_exceptions)
        return o

    def _load_plugins(self, invoke_on_load, invoke_args, invoke_kwds,
                      names=None):
        try:
            return super(DriverManager, self)._load_plugins(
                invoke_on_load,
                invoke_args,
                invoke_kwds,
                names,
                catch_exception=False)
        except Exception as err:
            raise RuntimeError(
                'Unable to load driver %s from %s: %s' %
                (names[0], self.namespace, err))

    def _init_plugins(self, extensions):
        super(DriverManager, self)._init_plugins(extensions)

        if not self.extensions:
            name = self._names[0]
            raise RuntimeError('No %r driver found, looking for %r' %
                               (self.namespace, name))
        if len(self.extensions) > 1:
            discovered_drivers = ','.join(e.entry_point_target
                                          for e in self.extensions)

            raise RuntimeError('Multiple %r drivers found: %s' %
                               (self.namespace, discovered_drivers))

    def __call__(self, func, *args, **kwds):
        """Invokes func() for the single loaded extension.

        The signature for func() should be::

            def func(ext, *args, **kwds):
                pass

        The first argument to func(), 'ext', is the
        :class:`~stevedore.extension.Extension` instance.

        Exceptions raised from within func() are logged and ignored.

        :param func: Callable to invoke for each extension.
        :param args: Variable arguments to pass to func()
        :param kwds: Keyword arguments to pass to func()
        :returns: List of values returned from func()
        """
        results = self.map(func, *args, **kwds)
        if results:
            return results[0]

    @property
    def driver(self):
        """Returns the driver being used by this manager.
        """
        ext = self.extensions[0]
        return ext.obj if ext.obj else ext.plugin
