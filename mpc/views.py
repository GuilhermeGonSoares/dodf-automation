from django.http import Http404, JsonResponse
from django.shortcuts import render
from .models import *
from user.models import UserProfile
from django.contrib.auth.decorators import login_required
import json
from .service import get_analise_by_dodf_id
from .cache import get_cached_publicacoes
from datetime import datetime
from .service import get_all_publicacoes_by_demandante


@login_required(login_url='user:login', redirect_field_name='next')
def dashboard(request):
    data_publicacao = request.GET.get('data_publicacao')
    current_date = datetime.now().date()
    if data_publicacao:
        data = datetime.strptime(data_publicacao, "%Y-%m-%d").date()
    else:
        data = current_date

    user_profile = UserProfile.objects.prefetch_related('jurisdicionadas').get(user=request.user)
    jurisdicionadas = user_profile.jurisdicionadas.all()
    coDemandantes = jurisdicionadas.values_list('coDemandante', flat=True)
    dic = get_cached_publicacoes(coDemandantes, user_profile.id, data)
    
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
    if data_publicacao:
        data = datetime.strptime(data_publicacao, "%Y-%m-%d").date()
    else:
        data = datetime.now().date()

    user_profile = UserProfile.objects.prefetch_related('jurisdicionadas').get(user=request.user)
    jurisdicionadas = user_profile.jurisdicionadas.all()
    coDemandantes = [jurisdicionada.coDemandante for jurisdicionada in jurisdicionadas if jurisdicionada.coDemandante != '']
    dic = get_cached_publicacoes(coDemandantes, user_profile.id, data)
    current_jurisdicionada = [jurisdicionada for jurisdicionada in jurisdicionadas if jurisdicionada.coDemandante==coDemandante][0]
    
    publicacoes = dic[coDemandante]
    return render(request, 'pages/publicacao.html', {
        'noticias': publicacoes,
        'jurisdicionada': current_jurisdicionada,
        'publicacao_cadastrada': {},
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


def jurisdicionada_detail(request):
    jurisdicionada_id = request.GET.get('id')
    page_number = request.GET.get('page', 1)
    jurisdicionada = Jurisdicionada.objects.get(pk=jurisdicionada_id)

    page_results = get_all_publicacoes_by_demandante(jurisdicionada, page_number)

    return render(request, 'pages/jurisdicionada-detail.html', {
        'page_results': page_results, 
        'jurisdicionada_id': jurisdicionada_id
        })
