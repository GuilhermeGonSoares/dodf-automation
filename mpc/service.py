from .models import DodfPublicacao, PublicacaoAnalisada
from datetime import date
from django.db import connection


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

def get_publicacoes(coDemandantes, data):
    dic = {}
    for jurisdicionada in coDemandantes:
        descendentes = get_descendants(jurisdicionada, [j for j in coDemandantes if j != jurisdicionada])
        publicacoes = publicacao_por_demandante(descendentes, 'III', data)
        dic[jurisdicionada] = publicacoes
        
    return dic