from .models import DodfPublicacao, PublicacaoAnalisada, Jurisdicionada
from django.db import connection
from django.db.models import F
from django.core.paginator import Paginator

def publicacao_por_demandante(demandantes, secao, data):

    resultado = DodfPublicacao.objects.select_related('publicacaoanalisada').filter(
        coDemandante__in=demandantes,
        secao=secao,
        carga__date=data
    )

    return resultado

def get_analise_by_dodf_id(id):
    return PublicacaoAnalisada.objects.filter(dodf_id=id).first()

def get_descendants(co_demandante, exclusions_list):
    query = """
    WITH descendants AS (
        SELECT coDemandante, coDemandantePai
        FROM demandante
        WHERE coDemandante = %s

        UNION ALL

        SELECT d.coDemandante, d.coDemandantePai
        FROM demandante d
        JOIN descendants pd ON d.coDemandantePai = pd.coDemandante
        WHERE d.coDemandantePai NOT IN (%s)
    )
    SELECT coDemandante
    FROM descendants
    WHERE coDemandante NOT IN (%s);
    """

    with connection.cursor() as cursor:
        exclusions = ",".join(map(str, exclusions_list))
        cursor.execute(query, (co_demandante, exclusions, exclusions))
        results = cursor.fetchall()
        descendants = [row[0] for row in results]

    return descendants

def get_publicacoes_by_day(coDemandantes, data):
    dic = {}
    for jurisdicionada in coDemandantes:
        descendentes = get_descendants(jurisdicionada, [j for j in coDemandantes if j != jurisdicionada])
        publicacoes = publicacao_por_demandante(descendentes, 'III', data)
        dic[jurisdicionada] = publicacoes
        
    return dic

def get_all_publicacoes_by_demandante(jurisdicionada, page_number):
    descendentes = get_descendants(jurisdicionada.coDemandante, [])

    # Primeiro, pré-carregue as informações das Jurisdicionadas relacionadas
    co_demandantes = DodfPublicacao.objects.filter(
        coDemandante__in=descendentes,
        secao__in=['I', 'III']
    ).values_list('coDemandante', flat=True)
    
    jurisdicionadas = Jurisdicionada.objects.filter(coDemandante__in=co_demandantes)

    # Crie um dicionário mapeando coDemandante para Jurisdicionada
    co_demandante_to_jurisdicionada = {jur.coDemandante: jur for jur in jurisdicionadas}

    # Agora, faça a consulta das publicações com paginação
    resultado = DodfPublicacao.objects.filter(
        coDemandante__in=descendentes,
        secao__in=['I', 'III']
    ).order_by(F('carga').desc())
    
    items_per_page = 10 
    paginator = Paginator(resultado, items_per_page)

    try:
        page_results = paginator.page(page_number)
    except:
        page_results = paginator.page(paginator.num_pages)

    # Atribua as informações da Jurisdicionada a cada publicação
    for publicacao in page_results:
        co_demandante = publicacao.coDemandante
        jurisdicionada = co_demandante_to_jurisdicionada.get(co_demandante)
        publicacao.jurisdicionada = jurisdicionada

    return page_results