#!/usr/bin/python
import time

def memoize(fn):
    cache = {}

    def inner(*args):
        try:
            return cache[args]
        except KeyError:
            result = cache[args] = fn(*args)
            return result
        except TypeError:
            print 'Can not hash: {}.'.format(','.join([str(a) for a in args]))
            return fn(*args)
    return inner

def timeit(fn):
    name = fn.__name__

    def timed(*args, **kwargs):
        ts = time.time()
        result = fn(*args, **kwargs)
        te = time.time()
        print 'func: %r took: %2.4f sec' % (name, te-ts)
        return result

    return timed
