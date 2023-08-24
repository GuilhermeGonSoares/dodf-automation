from .models import DodfPublicacao, PublicacaoAnalisada, Demandante
from django.db import connection
from math import ceil
from django.db.models import OuterRef, Subquery

def publicacao_por_demandante(demandantes, secao, data):
    nome_subquery = Demandante.objects.filter(
        coDemandante=OuterRef('coDemandante')
    ).values('nome')[:1]

    resultado = DodfPublicacao.objects.annotate(
        nome_demandante=Subquery(nome_subquery)
    ).select_related('publicacaoanalisada').filter(
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



def get_total_pages(jurisdicionada, results_per_page=10):
    query = """
    WITH descendants AS (
        SELECT coDemandante
        FROM demandante
        WHERE coDemandante = %s
        UNION ALL
        SELECT d.coDemandante
        FROM demandante d
        JOIN descendants pd ON d.coDemandantePai = pd.coDemandante
    )
    SELECT COUNT(dp.id)  
    FROM dodfPublicacao dp 
    INNER JOIN descendants des ON des.coDemandante = dp.coDemandante
    WHERE secao != 'II';
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [jurisdicionada.coDemandante])
        total = cursor.fetchone()[0]

    return ceil(total / results_per_page)
    

def get_all_publicacoes_by_demandante(jurisdicionada, page_number, results_per_page=10):
        offset = (page_number - 1) * results_per_page

        query = """
        WITH descendants AS (
            SELECT coDemandante
            FROM demandante
            WHERE coDemandante = %s

            UNION ALL

            SELECT d.coDemandante
            FROM demandante d
            JOIN descendants pd ON d.coDemandantePai = pd.coDemandante
        )

        SELECT d.nome, dp.coDemandante, dp.secao, dp.tipo, dp.titulo, dp.texto, pa.comentario, dp.carga  
        FROM dodfPublicacao dp 
        INNER JOIN descendants des ON des.coDemandante = dp.coDemandante
        INNER JOIN demandante d ON d.coDemandante = dp.coDemandante
        LEFT JOIN publicacao_analisada pa ON pa.dodf_id = dp.id
        WHERE secao != 'II'
        ORDER BY carga DESC
        OFFSET %s ROWS FETCH NEXT %s ROWS ONLY;
        """

        with connection.cursor() as cursor:
            cursor.execute(query, (jurisdicionada.coDemandante, offset, results_per_page))
            results = cursor.fetchall()
            

        # Transforme os resultados em objetos e retorne
        objects = []
        for row in results:
            obj = {
                'nome': row[0],
                'coDemandante': row[1],
                'secao': row[2],
                'tipo': row[3],
                'titulo': row[4],
                'texto': row[5],
                'comentario': row[6],
                'carga': row[7].strftime('%d/%m/%Y')
            }
            objects.append(obj)

        return objects