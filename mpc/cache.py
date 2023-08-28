from django.core.cache import cache
from .service import get_descendants


def get_cached_jurisdicionadas_with_descendentes(coDemandante, jurisdicionadas):
    cache_key = f"jurisdicionadas-descendentes"
    cached_result = cache.get(cache_key)
    
    if not cached_result:
        cached_result = {}

    if cached_result.get(coDemandante, None):
        print('oia o cache', cached_result.get(coDemandante))
        return cached_result.get(coDemandante)
    
    descendentes = get_descendants(coDemandante, [code for code in jurisdicionadas if code != coDemandante])
    cached_result[coDemandante] = descendentes

    
    cache.set(cache_key, cached_result, 86400)
    return cached_result[coDemandante]