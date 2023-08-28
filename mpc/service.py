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
    
    formatted_ids = ", ".join(["'" + str(id) + "'" for id in exclusions_list])

    query = f"""
    WITH descendants AS (
        SELECT coDemandante, coDemandantePai
        FROM demandante
        WHERE coDemandante = {co_demandante}

        UNION ALL

        SELECT d.coDemandante, d.coDemandantePai
        FROM demandante d
        JOIN descendants pd ON d.coDemandantePai = pd.coDemandante
        WHERE d.coDemandantePai NOT IN ({formatted_ids})
    )
    SELECT coDemandante
    FROM descendants
    WHERE coDemandante NOT IN ({formatted_ids});
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
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


def get_all_jurisdicionadas():
    query = """
        SELECT coDemandante FROM jurisdicionada j 
        ORDER BY CAST(coDemandante AS INTEGER);
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        results = cursor.fetchall()
        co_jurisdicionadas = [int(row[0]) for row in results if row[0]]
    
    return co_jurisdicionadas

def binary_search(array, value):
    i = 0
    j = len(array) - 1
    
    while i <= j:
        middle = (i + j) // 2
        if array[middle] == value:
            array.pop(middle)
            return array
        else:
            if array[middle] < value:
                i = middle + 1
            else:
                j = middle - 1
    return array