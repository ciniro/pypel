from cadastros.models import Usuario
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def rel_funcionarios(request):    
    funcionarios_lista = Usuario.objects.all()
    return render(request, 'rel_funcionarios.html', {'funcionarios_lista': funcionarios_lista})