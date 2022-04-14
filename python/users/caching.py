import redis
import pickle
from functools import wraps


def cache(redis: redis.Redis, key: str):
    """
    Caches the result of the function in redis and pickle, used a key to cache it

    :param redis: a redis configured instance
    :param key: the key to use as a parameter for the cache
    :return: the result of the wrapped function
    """

    def decorator(fn):  # define a decorator for a function "fn"
        @wraps(fn)
        def wrapped(
            *args, **kwargs
        ):  # define a wrapper that will finally call "fn" with all arguments
            # if cache exists -> load it and return its content
            cached = redis.get(kwargs[key])
            if cached:
                return pickle.loads(cached)
            # execute the function with all arguments passed
            res = fn(*args, **kwargs)
            # save cache in redis
            redis.set(kwargs[key], pickle.dumps(res))
            return res

        return wrapped

    return decorator


def cache_invalidate(redis: redis.Redis, key: str):
    """
    Deletes the redis cache by the key specified

    :param redis: a redis configured instance
    :param key: the key to use as a parameter for the cache deletion
    :return: the result of the wrapped function
    """

    def decorator(fn):  # define a decorator for a function "fn"
        @wraps(fn)
        def wrapped_f(
            *args, **kwargs
        ):  # define a wrapper that will finally call "fn" with all arguments
            # execute the function with all arguments passed
            res = fn(*args, **kwargs)
            # delete cache
            redis.delete(kwargs[key])
            return res

        return wrapped_f

    return decorator
