from django.core.cache import cache
from .service import get_descendants


def get_cached_descendentes(co_demandante, exclusions_list) :
    cache_key = f"descendentes-{co_demandante}"
    cached_result = cache.get(cache_key)

    if cached_result:
        print('tomali o cache')
        return cached_result
    
    result = get_descendants(co_demandante,  exclusions_list)
    
    cache.set(cache_key, result, 86400)
    return result