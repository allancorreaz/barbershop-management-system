
# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class Cliente(models.Model):
    SEXO_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    )
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nome = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()
    endereco = models.TextField(blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nome
    
    def idade(self):
        today = timezone.now().date()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))

class Acompanhante(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='acompanhantes')
    nome = models.CharField(max_length=100)
    idade = models.IntegerField()
    parentesco = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.nome} ({self.parentesco})"

class Barbeiro(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()
    comissao = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

class Servico(models.Model):
    CATEGORIA_CHOICES = (
        ('CORTE', 'Corte'),
        ('BARBA', 'Barba'),
        ('SOBRANCELHA', 'Sobrancelha'),
        ('PIGMENTACAO', 'Pigmentação'),
        ('OUTRO', 'Outro'),
    )
    
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    preco = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    duracao = models.DurationField(help_text="Duração estimada do serviço em minutos")
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - R${self.preco}"

class Promocao(models.Model):
    nome = models.CharField(max_length=100)
    servicos = models.ManyToManyField(Servico)
    desconto = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    data_inicio = models.DateField()
    data_fim = models.DateField()
    descricao = models.TextField(blank=True, null=True)
    
    def preco_total(self):
        total = sum(servico.preco for servico in self.servicos.all())
        return total - (total * (self.desconto / 100))
    
    def __str__(self):
        return f"{self.nome} - {self.desconto}% de desconto"

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco_compra = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    preco_venda = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    quantidade = models.IntegerField(validators=[MinValueValidator(0)])
    quantidade_minima = models.IntegerField(validators=[MinValueValidator(0)])
    fornecedor = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nome} - Estoque: {self.quantidade}"
    
    def precisa_repor(self):
        return self.quantidade < self.quantidade_minima

class Atendimento(models.Model):
    STATUS_CHOICES = (
        ('AGENDADO', 'Agendado'),
        ('CONCLUIDO', 'Concluído'),
        ('CANCELADO', 'Cancelado'),
        ('FALTOU', 'Faltou'),
    )
    
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    barbeiro = models.ForeignKey('Barbeiro', on_delete=models.CASCADE)
    servicos = models.ManyToManyField('Servico')
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')
    valor_total = models.DecimalField(max_digits=8, decimal_places=2)
    observacoes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.cliente} - {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
    
    def calcular_total(self):
        return sum(servico.preco for servico in self.servicos.all())
    
    def save(self, *args, **kwargs):
        if not self.valor_total:
            self.valor_total = self.calcular_total()
        super().save(*args, **kwargs)

class MovimentacaoCaixa(models.Model):
    TIPO_CHOICES = (
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    )
    
    CATEGORIA_CHOICES = (
        ('ATENDIMENTO', 'Atendimento'),
        ('PRODUTO', 'Venda de Produto'),
        ('DESPESA', 'Despesa'),
        ('OUTRO', 'Outro'),
    )
    
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    valor = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    atendimento = models.ForeignKey(Atendimento, on_delete=models.SET_NULL, null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descricao} - R${self.valor}"

class Comissao(models.Model):
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name='comissoes')  
    atendimento = models.ForeignKey(Atendimento, on_delete=models.CASCADE)
    valor = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    paga = models.BooleanField(default=False)
    data_pagamento = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.barbeiro} - R${self.valor} - {'Paga' if self.paga else 'Pendente'}"
    
    def calcular_comissao(self):
        return self.atendimento.valor_total * (self.barbeiro.comissao / 100)
    
    def save(self, *args, **kwargs):
        if not self.valor:
            self.valor = self.calcular_comissao()
        super().save(*args, **kwargs)