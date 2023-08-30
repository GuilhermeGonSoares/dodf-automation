# Usar uma imagem base do Python
FROM python:3.9

# Instalar as dependências necessárias para adicionar repositórios Microsoft
RUN apt-get update && apt-get install -y curl gnupg

# Adicionar as chaves e fontes para instalar o ODBC Driver 17 para SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Instalar o ODBC Driver
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Definir o diretório de trabalho
WORKDIR /app

# Copiar o arquivo de requerimentos e instalar as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos da aplicação
COPY . .

# Expor a porta do Django (altere para a porta que você usa, se não for 8000)
EXPOSE 8000

# Definir o comando padrão para executar sua aplicação
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]