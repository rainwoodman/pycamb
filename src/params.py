import numpy

class P(object):
    def __init__(self, name, fname, doc='', type=float, default=None):
        self.name = name 
        self.__doc__ = doc
        self.fname = fname
        self.type = type
        self.default = default

    def __repr__(self):
        typestr = {
                float: 'f',
                int: 'i',
                bool: 'b',
                }
        return '%(name)s [%(type)s:%(default)s] %(doc)s (%(fname)s)' % \
                dict(name=self.name,
                        doc=self.__doc__,
                        fname=self.fname,
                        default=str(self.default),
                        type=typestr[self.type])

class BoundParams(numpy.ndarray):
    def __new__(self, params, kwargs):
        vector = numpy.zeros(1024, 'f8')
        self = vector.view(type=BoundParams)

        self.params = params
        self.lookup = {}

        n = set([p.name for p in params])
        for key in kwargs:
            if key not in n:
                raise KeyError(
            "`%s' is unsupported. Supported parameters are: %s " \
            % (key, ', '.join(n)))

        # lets see if any kwargs are unsupported:
        #
        for i, p in enumerate(params):
            if p.name in kwargs:
                vector[i] = kwargs[p.name]
            else:
                if p.default is not None:
                    vector[i] = p.default
                else:
                    vector[i] = numpy.nan
            self.lookup[p.name] = vector[i]
        return self
    @property
    def keys(self):
        return self.lookup.keys()

    def __getitem__(self, index):
        return self.lookup[index]

    def __repr__(self):
        return '\n'.join([
            "%(name)s = %(value)f" % dict(
                name=key, value=self[key]) 
            for key in self.keys
            ])

class Params(list):
    def __init__(self, l):
        list.__init__(self, l)

    def __repr__(self):
        return '\n'.join([str(p) for p in self])

    def __call__(self, **kwargs):
        return BoundParams(self, kwargs)
