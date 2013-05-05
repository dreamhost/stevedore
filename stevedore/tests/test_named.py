from stevedore import named

import mock


def test_named():
    em = named.NamedExtensionManager(
        'stevedore.test.extension',
        names=['t1'],
        invoke_on_load=True,
        invoke_args=('a',),
        invoke_kwds={'b': 'B'},
    )
    actual = em.names()
    assert actual == ['t1']


def test_enabled_before_load():
    # Set up the constructor for the FauxExtension to cause an
    # AssertionError so the test fails if the class is instantiated,
    # which should only happen if it is loaded before the name of the
    # extension is compared against the names that should be loaded by
    # the manager.
    init_name = 'stevedore.tests.test_extension.FauxExtension.__init__'
    with mock.patch(init_name) as m:
        m.side_effect = AssertionError
        em = named.NamedExtensionManager(
            'stevedore.test.extension',
            # Look for an extension that does not exist so the
            # __init__ we mocked should never be invoked.
            names=['no-such-extension'],
            invoke_on_load=True,
            invoke_args=('a',),
            invoke_kwds={'b': 'B'},
        )
        actual = em.names()
        assert actual == []
