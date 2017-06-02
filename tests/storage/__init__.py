"""
Unittests for the dbus-storage backend.

At first glance it may seem strange that we add mocked service methods not as
part of the test setup but in each individual test. This is due to
``dbus-python``s strange way to handle mocking return values. Whilst all tests
related to a particular test class deal with the same method, they may expect
different return values specific to their test goals. As ``AddMethod`` does not
really seem to allow for dynamic return values it seems cleaner and more
transparent to provide them with each individual test explicitly.

Please not that the unit tests included here do *mock* the underlying dbus
service.  This mean in particular that they make assumptions about the services
signature.  As a consequence those tests will not be able to make sure that the
tested storage backend will actually work against a given service implementation
(such as provided by ``hamster_dbus.objects``). For this to be tested, dedicated
integration tests are needed.

Most manager methods really only call the relevant de/serialization functions
before/after the respective dbus object method call. As the method call itself
is mocked, and the de/serialization functions are tested separately there is
relatively little to test here for now and we mainly make sure that the returned
types match our expectation. Still, even those basic test coverage will provide
useful guards against regression bugs as they ensure the relevant manager
methods are called at least once.
"""
