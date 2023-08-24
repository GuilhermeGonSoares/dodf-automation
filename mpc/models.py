from django.db import models

class Unidade(models.Model):
    class Meta:
        managed = False
        db_table = 'unidade'

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=50)
    sigla = models.CharField(max_length=3)
    titular = models.CharField(max_length=80)
    email = models.CharField(max_length=80)
    ramal = models.CharField(max_length=15)

    def __str__(self):
        return self.nome


class Jurisdicionada(models.Model):
    class Meta:
        managed = False
        db_table = 'jurisdicionada'

    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=255)
    coDemandante = models.CharField(max_length=255, unique=True)
    sigla = models.CharField(max_length=20)
    unidade = models.ForeignKey(Unidade, on_delete=models.CASCADE)
    apelido = models.CharField(max_length=50)
    vl_bens_serv = models.DecimalField(max_digits=12, decimal_places=2)
    vl_obras_eng = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.nome


class Demandante(models.Model):
    class Meta:
        managed = False
        db_table = 'demandante'
    id = models.AutoField(primary_key=True)
    coDemandante = models.CharField(max_length=255)
    coDemandantePai = models.CharField(max_length=255)

    def __str__(self):
        return self.coDemandante


class DodfPublicacao(models.Model):
    class Meta:
        managed = False
        db_table = 'dodfPublicacao'  # Nome da tabela no banco de dados

    id = models.AutoField(primary_key=True)
    coMateria = models.CharField(max_length=255)
    coDemandante = models.CharField(max_length=255)
    secao = models.CharField(max_length=10)
    titulo = models.CharField(max_length=255)
    preambulo = models.TextField()  # Use TextField para campos NVARCHAR(MAX)
    tipo = models.CharField(max_length=255)
    situacao = models.CharField(max_length=255)
    regraSituacao = models.CharField(max_length=255)
    layout = models.CharField(max_length=255)
    nuOrdem = models.CharField(max_length=255)
    texto = models.TextField()  # Use TextField para campos NVARCHAR(MAX)
    carga = models.DateTimeField()

    def __str__(self) -> str:
        return f'{self.coDemandante}: -> {self.titulo}'


class PublicacaoAnalisada(models.Model):
    class Meta:
        db_table = 'publicacao_analisada'
    
    user = models.ForeignKey('user.UserProfile', null=True, on_delete=models.SET_NULL)
    dodf = models.OneToOneField(DodfPublicacao, null=True, on_delete=models.SET_NULL)
    comentario=models.TextField(null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)