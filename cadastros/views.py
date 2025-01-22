from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, F, Count, Subquery, OuterRef, FloatField, Sum, ExpressionWrapper
from .models import Usuario, Perfil, Departamento
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Coalesce
from django.http import HttpResponse

#CADASTRO DE DEPARTAMENTOS
@login_required
def departamentos(request):
    if request.session.get('perfil_atual') not in {'Administrador'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')
    
    if request.method == "POST":
        acao = request.POST.get("btnAcao")

        if acao == "novo_departamento":
            nome = request.POST.get('txtNome')
            
            if (nome == 'Geral'):
                messages.error(request, 'Você não pode cadastrar um departamento chamado "Geral", pois esse nome é reservado para o sistema! Use outro.')
                return redirect('cadastros:departamentos')
            
            sigla = request.POST.get('txtSigla')

            if Departamento.objects.filter(nome=nome).exists():
                messages.error(request, 'Nome de departamento já cadastrado nesta unidade!')
                return redirect('cadastros:departamentos')

            departamento = Departamento(
                nome=nome,
                sigla=sigla,
            )
            
            departamento.save()

            messages.success(request, 'Departamento cadastrado com sucesso!')
            return redirect('cadastros:departamentos')

        elif acao == "alterar_departamento":
            departamento_id = request.POST.get('txtId')
            departamento = Departamento.objects.get(id=departamento_id)

            nome = request.POST.get('txtNome')
            
            if (nome == 'Geral'):
                messages.error(request, 'Você não pode cadastrar um departamento chamado "Geral", pois esse nome é reservado para o sistema! Use outro.')
                return redirect('cadastros:departamentos')
            
            sigla = request.POST.get('txtSigla')
            
            if Departamento.objects.filter(nome=nome).exclude(id=departamento_id).exists():
                messages.error(request, 'nome de departamento ja cadastrado nesta unidade!')
                return redirect('cadastros:departamentos')
            
            departamento.nome = nome
            departamento.sigla = sigla

            departamento.save()

            messages.success(request, 'Departamento atualizado com sucesso!')
            return redirect('cadastros:departamentos')

    departamento_lista = Departamento.objects.all().exclude(nome__iexact="Geral").order_by('nome')

    paginator = Paginator(departamento_lista, settings.NUMBER_GRID_PAGES)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    return render(request, "departamentos.html", {'page_obj': page_obj})

@login_required
def obter_departamento_por_id(request):
    departamento_id = request.GET.get('departamento_id', None)
    departamento = Departamento.objects.get(id=departamento_id)
    
    departamento_dados = {
        'id': departamento.id,
        'nome': departamento.nome,
        'sigla': departamento.sigla,
    }

    return JsonResponse(departamento_dados)

@login_required
def excluir_departamento(request):
    if request.method == "POST":
        departamento_id = request.POST.get('departamento_id')
        departamento = Departamento.objects.filter(id=departamento_id).first()

        if (departamento.usuario_set.exists()):  
            return JsonResponse({'success': False, 'message': "Não é possível excluir o departamento, pois ele possui usuários vinculados."})

        departamento.delete()
        return JsonResponse({'success': True, 'message': 'Departamento excluído com sucesso!'})
    
    return JsonResponse({'success': False, 'message': 'Você não tem permissão para acesso.'}, status=405)
    
@login_required
def pesquisar_departamento_por_nome(request):
    departamento_nome = request.GET.get('departamento_nome', '')
    numero_pagina = request.GET.get('page')

    departamento_lista = Departamento.objects.filter(nome__icontains=departamento_nome).exclude(nome__iexact="Geral").order_by('nome')

    paginator = Paginator(departamento_lista, settings.NUMBER_GRID_PAGES)
    page_obj = paginator.get_page(numero_pagina)

    return JsonResponse({
        'html': render_to_string('departamentos_table.html', {'page_obj': page_obj, 'query': departamento_nome, 'request': request})
    })
