from django.core.cache import cache
from .service import get_publicacoes
from datetime import datetime

def get_cached_publicacoes(coDemandantes, user_profile_id, data):
    cache_key = f"publicacoes-{data.day}-{data.month}-{data.year}-{user_profile_id}"
    cached_result = cache.get(cache_key)

    if cached_result:
        return cached_result

    result = get_publicacoes(coDemandantes,  data)
    # Armazena o resultado no cache por 24 horas (86400 segundos)
    cache.set(cache_key, result, 86400)
    return result
