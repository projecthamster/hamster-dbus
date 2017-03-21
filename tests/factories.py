"""Factories to provide easy to use randomized instances of our main objects."""

import datetime

import factory
import fauxfactory
import hamster_lib


class CategoryFactory(factory.Factory):
    """Provide a factory for randomized ``hamster_lib.Category`` instances."""

    pk = None
    name = fauxfactory.gen_utf8()

    class Meta:
        model = hamster_lib.Category


class TagFactory(factory.Factory):
    """Provide a factory for randomized ``hamster_lib.Tag`` instances."""

    pk = None
    name = fauxfactory.gen_utf8()

    class Meta:
        model = hamster_lib.Tag


class ActivityFactory(factory.Factory):
    """Provide a factory for randomized ``hamster_lib.Activity`` instances."""

    pk = None
    name = fauxfactory.gen_utf8()
    category = factory.SubFactory(CategoryFactory)
    deleted = False

    class Meta:
        model = hamster_lib.Activity


class FactFactory(factory.Factory):
    """Provide a factory for randomized ``hamster_lib.Fact`` instances."""

    pk = None
    activity = factory.SubFactory(ActivityFactory)
    start = factory.Faker('date_time')
    end = factory.LazyAttribute(lambda o: o.start + datetime.timedelta(
        hours=3))
    description = factory.Faker('paragraph')

    class Meta:
        model = hamster_lib.Fact
