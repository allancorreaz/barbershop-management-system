from django.urls import path
from . import views

urlpatterns = [
    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Clientes
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/novo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/', views.ClienteDetailView.as_view(), name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/excluir/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
    
    # Serviços
    path('servicos/', views.ServicoListView.as_view(), name='servico_list'),
    path('servicos/novo/', views.ServicoCreateView.as_view(), name='servico_create'),
    path('servicos/<int:pk>/editar/', views.ServicoUpdateView.as_view(), name='servico_update'),
    path('servicos/<int:pk>/excluir/', views.ServicoDeleteView.as_view(), name='servico_delete'),
    
    # Atendimentos
    path('atendimentos/', views.AtendimentoListView.as_view(), name='atendimento_list'),
    path('atendimentos/novo/', views.AtendimentoCreateView.as_view(), name='atendimento_create'),
    path('atendimentos/<int:pk>/editar/', views.AtendimentoUpdateView.as_view(), name='atendimento_update'),
    
    # Caixa
    path('caixa/', views.caixa_dashboard, name='caixa_dashboard'),
    path('caixa/movimentacao/nova/', views.MovimentacaoCreateView.as_view(), name='movimentacao_create'),
    
    # Estoque
    path('estoque/', views.ProdutoListView.as_view(), name='produto_list'),
    path('estoque/novo/', views.ProdutoCreateView.as_view(), name='produto_create'),
    path('estoque/<int:pk>/editar/', views.ProdutoUpdateView.as_view(), name='produto_update'),
    
    # Relatórios
    path('relatorios/clientes/', views.relatorio_clientes, name='relatorio_clientes'),
    path('relatorios/servicos/', views.relatorio_servicos, name='relatorio_servicos'),
]