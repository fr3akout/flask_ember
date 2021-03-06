from flask_ember.util.string import underscore


OPTIONS = [
    # the name of the generated table (is taken into account before
    # tablename_generator)
    ('tablename', None),
    # a function that takes the model class name and returns the table name
    ('tablename_generator', underscore)
]


class ResourceOptions:
    def __init__(self, meta=None, options=None):
        meta = meta or type('Meta', (), dict())
        options = options or OPTIONS

        for option_key, default_value in options:
            setattr(self, option_key, getattr(meta, option_key, default_value))

    def __repr__(self):
        return str(self.__dict__)
