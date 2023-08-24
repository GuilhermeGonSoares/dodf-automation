from django.core.cache import cache
from .service import get_descendants


def get_cached_descendentes(co_demandante, exclusions_list) :
    cache_key = f"descendentes-{co_demandante}"
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result
    
    result = get_descendants(co_demandante,  exclusions_list)
    
    cache.set(cache_key, result, 86400)
    return result

def get_cached_jurisdicionadas_with_descendentes(user_profile):
    cache_key = f"jurisdicionadas-descendentes-{user_profile.id}"
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result
    
    dic = {}

    jurisdicionadas = user_profile.jurisdicionadas.all()
    coDemandantes = jurisdicionadas.values_list('coDemandante', flat=True)
    
    for jurisdicionada in coDemandantes:
        descendentes = get_cached_descendentes(jurisdicionada, [j for j in coDemandantes if j != jurisdicionada])
        dic[jurisdicionada] = descendentes
    
    cache.set(cache_key, dic, 86400)
    return dic