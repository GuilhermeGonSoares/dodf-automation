from django.http import Http404, JsonResponse
from django.shortcuts import render
from .models import *
from user.models import UserProfile
from django.contrib.auth.decorators import login_required
import json
from .service import get_analise_by_dodf_id
from datetime import datetime
from .service import get_all_publicacoes_by_demandante, get_total_pages, publicacao_por_demandante
from .cache import get_cached_jurisdicionadas_with_descendentes


def get_publicacoes_by_day(user_profile, data):
    dic = {}
    jurisdicionadas = get_cached_jurisdicionadas_with_descendentes(user_profile)
    for jurisdicionada in jurisdicionadas.keys():
        publicacoes = publicacao_por_demandante(jurisdicionadas[jurisdicionada], 'III', data)
        dic[jurisdicionada] = publicacoes
        
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
    dic = get_publicacoes_by_day(user_profile, data)
    
    
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
    dic = get_publicacoes_by_day(user_profile, data)
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
