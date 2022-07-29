from typing import Any, Union

from cache3 import SafeCache

from fastpt.common.log import log


class MemoryCache:

    def __init__(self, cache=SafeCache()):
        self.cache = cache

    def cache_get(self, key: str, **kwargs) -> Any:
        """
        获取缓存值

        :param key:
        :param kwargs:
        :return:
        """
        result = self.cache.get(key, **kwargs)
        if result:
            log.info(f'获取临时变量: {key}')
        return result

    def cache_set(self, key: Any, value: Any, **kwargs) -> bool:
        """
        设置缓存值

        :param key:
        :param value:
        :param kwargs:
        :return:
        """
        result = self.cache.set(key, value, **kwargs)
        if result:
            log.info(f'设置临时变量: {key} -> {value}')
        return result

    def cache_delete(self, key: str, **kwargs) -> bool:
        """
        删除缓存值

        :param key:
        :param kwargs:
        :return:
        """
        return self.cache.delete(key, **kwargs)

    def cache_has(self, key: str, **kwargs) -> bool:
        """
        是否存在缓存值

        :param key:
        :param kwargs:
        :return:
        """
        result = self.cache.has_key(key, **kwargs)  # noqa
        if result:
            log.info(f'存在临时变量: {key}')
        return result

    def cache_incr(self, key, **kwargs) -> Union[int, float]:
        """
        是否存在缓存值, 当不存在时触发 ValueError

        :param key:
        :param kwargs:
        :return:
        """
        result = self.cache.incr(key, **kwargs)
        if result:
            log.info(f'存在临时变量: {key}')
        return result

    def cache_clear(self) -> bool:
        """
        清空缓存值

        :return:
        """
        result = self.cache.clear()
        if result:
            log.info('清空临时变量')
        return result
