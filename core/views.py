
# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta

from .models import *
from .forms import *

# Autenticação
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# Dashboard
@login_required
def dashboard(request):
    # Estatísticas básicas
    total_clientes = Cliente.objects.count()
    total_atendimentos = Atendimento.objects.filter(status='CONCLUIDO').count()
    total_servicos = Servico.objects.count()
    
    # Receitas do mês atual
    hoje = timezone.now()
    inicio_mes = hoje.replace(day=1)
    receita_mes = MovimentacaoCaixa.objects.filter(
        tipo='ENTRADA',
        data__gte=inicio_mes
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Atendimentos recentes
    atendimentos_recentes = Atendimento.objects.filter(
        status='CONCLUIDO'
    ).order_by('-data_hora')[:5]
    
    # Produtos para repor
    produtos_repor = Produto.objects.filter(quantidade__lt=models.F('quantidade_minima'))
    
    context = {
        'total_clientes': total_clientes,
        'total_atendimentos': total_atendimentos,
        'total_servicos': total_servicos,
        'receita_mes': receita_mes,
        'atendimentos_recentes': atendimentos_recentes,
        'produtos_repor': produtos_repor,
    }
    return render(request, 'relatorios/dashboard.html', context)

# Clientes
class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) |
                Q(telefone__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset.order_by('nome')

class ClienteDetailView(LoginRequiredMixin, DetailView):
    model = Cliente
    template_name = 'clientes/detalhe.html'
    context_object_name = 'cliente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.get_object()
        
        # Histórico de atendimentos
        atendimentos = Atendimento.objects.filter(
            cliente=cliente,
            status='CONCLUIDO'
        ).order_by('-data_hora')
        
        # Frequência mensal
        frequencia = Atendimento.objects.filter(
            cliente=cliente,
            status='CONCLUIDO',
            data_hora__gte=timezone.now() - timedelta(days=365)
        ).values('data_hora__month').annotate(
            total=Count('id')
        ).order_by('data_hora__month')
        
        context['atendimentos'] = atendimentos
        context['frequencia'] = frequencia
        return context

class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/formulario.html'
    success_url = reverse_lazy('cliente_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cliente cadastrado com sucesso!')
        return super().form_valid(form)

class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/formulario.html'
    success_url = reverse_lazy('cliente_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Cliente atualizado com sucesso!')
        return super().form_valid(form)

class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'clientes/confirmar_exclusao.html'
    success_url = reverse_lazy('cliente_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Cliente excluído com sucesso!')
        return super().delete(request, *args, **kwargs)

# Serviços
class ServicoListView(LoginRequiredMixin, ListView):
    model = Servico
    template_name = 'servicos/lista.html'
    context_object_name = 'servicos'
    
    def get_queryset(self):
        return Servico.objects.filter(ativo=True).order_by('categoria', 'nome')

class ServicoCreateView(LoginRequiredMixin, CreateView):
    model = Servico
    form_class = ServicoForm
    template_name = 'servicos/formulario.html'
    success_url = reverse_lazy('servico_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Serviço cadastrado com sucesso!')
        return super().form_valid(form)

class ServicoUpdateView(LoginRequiredMixin, UpdateView):
    model = Servico
    form_class = ServicoForm
    template_name = 'servicos/formulario.html'
    success_url = reverse_lazy('servico_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Serviço atualizado com sucesso!')
        return super().form_valid(form)

class ServicoDeleteView(LoginRequiredMixin, DeleteView):
    model = Servico
    template_name = 'servicos/confirmar_exclusao.html'
    success_url = reverse_lazy('servico_list')
    
    def delete(self, request, *args, **kwargs):
        servico = self.get_object()
        servico.ativo = False
        servico.save()
        messages.success(request, 'Serviço desativado com sucesso!')
        return redirect(self.success_url)

# Atendimentos
class AtendimentoListView(LoginRequiredMixin, ListView):
    model = Atendimento
    template_name = 'atendimentos/lista.html'
    context_object_name = 'atendimentos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        status = self.request.GET.get('status')
        data_inicio = self.request.GET.get('data_inicio')
        data_fim = self.request.GET.get('data_fim')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if data_inicio and data_fim:
            queryset = queryset.filter(data_hora__date__range=[data_inicio, data_fim])
        
        return queryset.order_by('-data_hora')

class AtendimentoCreateView(LoginRequiredMixin, CreateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = 'atendimentos/formulario.html'
    success_url = reverse_lazy('atendimento_list')
    
    def form_valid(self, form):
        atendimento = form.save(commit=False)
        atendimento.valor_total = atendimento.calcular_total()
        atendimento.save()
        form.save_m2m()  # Salva os serviços many-to-many
        
        # Cria movimentação no caixa
        MovimentacaoCaixa.objects.create(
            tipo='ENTRADA',
            categoria='ATENDIMENTO',
            valor=atendimento.valor_total,
            descricao=f"Atendimento #{atendimento.id}",
            atendimento=atendimento
        )
        
        # Calcula comissão do barbeiro
        Comissao.objects.create(
            barbeiro=atendimento.barbeiro,
            atendimento=atendimento,
            valor=atendimento.valor_total * (atendimento.barbeiro.comissao / 100)
        )
        
        messages.success(self.request, 'Atendimento registrado com sucesso!')
        return redirect(self.success_url)

class AtendimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Atendimento
    form_class = AtendimentoForm
    template_name = 'atendimentos/formulario.html'
    success_url = reverse_lazy('atendimento_list')
    
    def form_valid(self, form):
        atendimento = form.save(commit=False)
        atendimento.valor_total = atendimento.calcular_total()
        atendimento.save()
        form.save_m2m()
        
        messages.success(self.request, 'Atendimento atualizado com sucesso!')
        return redirect(self.success_url)

# Caixa
@login_required
def caixa_dashboard(request):
    hoje = timezone.now().date()
    
    # Movimentações do dia
    movimentacoes_hoje = MovimentacaoCaixa.objects.filter(
        data__date=hoje
    ).order_by('-data')
    
    # Totais
    total_entradas = movimentacoes_hoje.filter(tipo='ENTRADA').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    total_saidas = movimentacoes_hoje.filter(tipo='SAIDA').aggregate(
        total=Sum('valor')
    )['total'] or 0
    
    saldo_dia = total_entradas - total_saidas
    
    context = {
        'movimentacoes': movimentacoes_hoje,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'saldo_dia': saldo_dia,
        'hoje': hoje,
    }
    return render(request, 'caixa/dashboard.html', context)

class MovimentacaoCreateView(LoginRequiredMixin, CreateView):
    model = MovimentacaoCaixa
    form_class = MovimentacaoCaixaForm
    template_name = 'caixa/movimentacao_form.html'
    success_url = reverse_lazy('caixa_dashboard')
    
    def form_valid(self, form):
        messages.success(self.request, 'Movimentação registrada com sucesso!')
        return super().form_valid(form)

# Estoque
class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = 'estoque/lista.html'
    context_object_name = 'produtos'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro para produtos que precisam ser repostos
        repor = self.request.GET.get('repor')
        if repor:
            queryset = queryset.filter(quantidade__lt=models.F('quantidade_minima'))
        
        return queryset.order_by('nome')

class ProdutoCreateView(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'estoque/formulario.html'
    success_url = reverse_lazy('produto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto cadastrado com sucesso!')
        return super().form_valid(form)

class ProdutoUpdateView(LoginRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'estoque/formulario.html'
    success_url = reverse_lazy('produto_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return super().form_valid(form)

# Relatórios
@login_required
def relatorio_clientes(request):
    # Clientes mais frequentes
    clientes_frequentes = Cliente.objects.annotate(
        total_atendimentos=Count('atendimento')
    ).order_by('-total_atendimentos')[:10]
    
    # Clientes que mais gastaram
    clientes_gastadores = Cliente.objects.annotate(
        total_gasto=Sum('atendimento__valor_total')
    ).order_by('-total_gasto')[:10]
    
    # Clientes inativos (último atendimento há mais de 3 meses)
    tres_meses_atras = timezone.now() - timedelta(days=90)
    clientes_inativos = Cliente.objects.exclude(
        atendimento__data_hora__gte=tres_meses_atras
    ).distinct()
    
    context = {
        'clientes_frequentes': clientes_frequentes,
        'clientes_gastadores': clientes_gastadores,
        'clientes_inativos': clientes_inativos,
    }
    return render(request, 'relatorios/clientes.html', context)

@login_required
def relatorio_servicos(request):
    # Serviços mais solicitados
    servicos_populares = Servico.objects.annotate(
        total_atendimentos=Count('atendimento')
    ).order_by('-total_atendimentos')
    
    # Receita por serviço
    receita_servicos = Servico.objects.annotate(
        total_receita=Sum('atendimento__valor_total')
    ).order_by('-total_receita')
    
    context = {
        'servicos_populares': servicos_populares,
        'receita_servicos': receita_servicos,
    }
    return render(request, 'relatorios/servicos.html', context)