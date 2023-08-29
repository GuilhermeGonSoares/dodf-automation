from django.core.cache import cache
from .service import get_descendants, get_all_jurisdicionadas, remove_element_binary_search


def get_cached_all_jurisdicionadas():
    cache_key = f"all-jurisdicionadas"
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result
    
    jurisdicionadas = get_all_jurisdicionadas()
    cache.set(cache_key, jurisdicionadas, 86400)
    return jurisdicionadas


def get_cached_jurisdicionadas_with_descendentes(coDemandante):
    cache_key = f"jurisdicionadas-descendentes"
    cached_result = cache.get(cache_key)
    
    if not cached_result:
        cached_result = {}

    if cached_result.get(coDemandante, None):
        return cached_result.get(coDemandante)
    
    jurisdicionadas = get_cached_all_jurisdicionadas()
    descendentes = get_descendants(coDemandante, remove_element_binary_search(jurisdicionadas, int(coDemandante)))
    cached_result[coDemandante] = descendentes

    cache.set(cache_key, cached_result, 86400)
    return cached_result[coDemandante]