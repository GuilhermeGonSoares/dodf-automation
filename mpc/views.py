from django.http import Http404, JsonResponse
from django.shortcuts import render
from .models import *
from user.models import UserProfile
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from .service import get_all_publicacoes_by_demandante, get_total_pages, publicacao_por_demandante, get_analise_by_dodf_id
from .cache import get_cached_jurisdicionadas_with_descendentes
from django.db.models import Q, OuterRef, Subquery
from django.core.paginator import Paginator, EmptyPage

def get_publicacoes_by_day(coDemandantes, data):
    dic = {}

    for coDemandante in coDemandantes:
        descendentes = get_cached_jurisdicionadas_with_descendentes(
            coDemandante
        )
        publicacoes = publicacao_por_demandante(descendentes, 'III', data)
        dic[coDemandante] = publicacoes

    return dic


def convert_data_publicacao(data_publicacao):
    if data_publicacao:
        data = datetime.strptime(data_publicacao, "%Y-%m-%d").date()
    else:
        data = datetime.now().date()

    return data

@login_required(login_url='user:login', redirect_field_name='next')
def dashboard(request):
    data_publicacao = request.GET.get('data_publicacao')
    current_date = datetime.now().date()
    data = convert_data_publicacao(data_publicacao)

    user_profile = UserProfile.objects.prefetch_related('jurisdicionadas').get(user=request.user)
    jurisdicionadas = user_profile.jurisdicionadas.all()
    coDemandantes = jurisdicionadas.filter(~Q(coDemandante='')).values_list('coDemandante', flat=True)
    
    dic = get_publicacoes_by_day(coDemandantes, data)
    
    
    return render(request, 'pages/dashboard.html', {
        'jurisdicionadas': jurisdicionadas,
        'unidade': user_profile.unidades,
        'info': dic,
        'data': data_publicacao,
        'data_atual': f'{current_date.year}-{current_date.month}-{current_date.day}'
    })


@login_required(login_url='user:login')
def publicacao(request, coDemandante):
    data_publicacao = request.GET.get('data_publicacao')
    current_date = datetime.now().date()
    data = convert_data_publicacao(data_publicacao)

    user_profile = UserProfile.objects.prefetch_related('jurisdicionadas').get(user=request.user)
    jurisdicionadas = user_profile.jurisdicionadas.all() 
    coDemandantes = jurisdicionadas.filter(~Q(coDemandante='')).values_list('coDemandante', flat=True)
    
    dic = get_publicacoes_by_day(coDemandantes, data)
    current_jurisdicionada = [jurisdicionada for jurisdicionada in jurisdicionadas if jurisdicionada.coDemandante==coDemandante][0]
    
    publicacoes = dic[coDemandante]
    return render(request, 'pages/publicacao.html', {
        'noticias': publicacoes,
        'jurisdicionada': current_jurisdicionada,
        'publicacao_cadastrada': {},
        'data': data_publicacao,
        'data_atual': f'{current_date.year}-{current_date.month}-{current_date.day}'
    })


@login_required(login_url='user:login')
def save_publicacao(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        publicacao_id = data.get('noticia_id')
        comentario = data.get('comentario')

        publicacao_analisada = get_analise_by_dodf_id(publicacao_id)

        if (not publicacao_analisada):
            publicacao_analisada = PublicacaoAnalisada.objects.create(
                user = UserProfile.objects.get(user=request.user),
                dodf_id=publicacao_id,
                comentario=comentario,
            )
            publicacao_analisada.save()
        else:
            publicacao_analisada.comentario = comentario
            publicacao_analisada.save()
        
            
        return JsonResponse({'status': 'success', 'message': 'Comentário salvo com sucesso!'})

@login_required(login_url='user:login')
def delete_publicacao(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        publicacao_id = data.get('noticia_id')
        publicacao = get_analise_by_dodf_id(publicacao_id)
        if not publicacao:
            raise Http404("Publicação não encontrada!")
        publicacao.delete()
        return JsonResponse({'status': 'success', 'message': 'Comentário apagado com sucesso!'})
    
@login_required(login_url='user:login')
def autocomplete_jurisdicionada(request):
    term = request.GET.get('term')  # Termo digitado pelo usuário
    jurisdicionadas = Jurisdicionada.objects.filter(nome__icontains=term)[:10]  # Filtra as jurisdicionadas que contêm o termo
    results = [{'label': jurisdicionada.nome, 'value': jurisdicionada.id} for jurisdicionada in jurisdicionadas]
    return JsonResponse(results, safe=False)

@login_required(login_url='user:login')
def jurisdicionada_detail(request):
    jurisdicionada_id = request.GET.get('id')
    page_number = int(request.GET.get('page', 1))
    jurisdicionada = Jurisdicionada.objects.get(pk=jurisdicionada_id)
    
    page_results = get_all_publicacoes_by_demandante(jurisdicionada, page_number)
    
    total_pages = get_total_pages(jurisdicionada)

    return render(request, 'pages/jurisdicionada-detail.html', {
        'page_results': page_results, 
        'jurisdicionada_id': jurisdicionada_id,
        'current_page': page_number,
        'has_previous': page_number > 1,
        'has_next': page_number < total_pages,
        'total_pages': total_pages
    })


@login_required(login_url='user:login')
def search_info_jurisdicionada(request):
    search = request.GET.get('q')
    jurisdicionada_id=request.GET.get('jurisdicionada_id')
    
    if jurisdicionada_id:
        jurisdicionada = Jurisdicionada.objects.get(pk=jurisdicionada_id)
        demandantes = get_cached_jurisdicionadas_with_descendentes(jurisdicionada.coDemandante)
    
    
    data_publicacao = request.GET.get('data_publicacao')
    data = convert_data_publicacao(data_publicacao)
    nome_subquery = Demandante.objects.filter(
        coDemandante=OuterRef('coDemandante')
    ).values('nome')[:1]

    query = Q(~Q(secao='II'), Q(titulo__contains=search) | Q(texto__contains=search), carga__date=data)

    if jurisdicionada_id:
        query &= Q(coDemandante__in=demandantes)

    publicacoes_list = DodfPublicacao.objects.annotate(
        nome_demandante=Subquery(nome_subquery)
    ).select_related('publicacaoanalisada').filter(query).order_by('carga')

    paginator = Paginator(publicacoes_list, 10)  
    page = request.GET.get('page', 1)
    
    try:
        publicacoes = paginator.page(page)
    except EmptyPage:
        publicacoes = paginator.page(paginator.num_pages)
    return render(request, 'pages/search-publicacoes.html', {
        'page_results': publicacoes, 
        'current_page': publicacoes.number, 
        'total_pages': paginator.num_pages, 
        'has_previous': publicacoes.has_previous(), 
        'has_next': publicacoes.has_next(),
        'search': search,
        'data': data,
        'data_publicacao': data_publicacao
        })