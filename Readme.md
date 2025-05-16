## CRIAÇÃO DO PROJETO

# Gitlab
1. Crie uma conta no gitlab
2. Na página Home clique em new (repository) e crie um Repositório com nome ml_books, não esqueça de marcá-lo como public e criar gitignore, e salve a url do projeto
3. No windows crie uma pasta chamada ml_books onde será clonado o projeto.
4. Abra o programa git bash e acesse a pasta que você criou
C:\workspace\BigData\ml_books
5. execute o clone do projeto executando o comando ainda no git bash (cole a url do projeto no lugar da url abaixo)
git clone https://github.com/joabmartins/ml_books.git
6. Crie o arquivo gitignore e adicione o seguinte texto: (sem as aspas, isso vai ignorar a pasta logs na hora de comitar)
```
# logs
**/logs
```
7. Abra o VSCode > File > Open Folder e selecione a pasta do projeto (ml_books)
8. Se não tiver um terminal aberto no VSCode então acesse um: Terminal > New Terminal

<!---
Nesse ponto mostrar aos alunos como criar uma imagem simples no docker antes de explicar como criar usando docker compose (usa o ubuntu)
docker exec -it <nome imagem> bash
cat /etc/issue
lsb_release -a
cat etc/os-release
hostnamectl
-->

9. Usando outro terminal do Visual studio ou powershell/cmd do windows Baixe o docker compose do airflow (importante ser executado dentro da pasta ml_books)
Invoke-WebRequest -Uri "https://airflow.apache.org/docs/apache-airflow/3.0.1/docker-compose.yaml" -OutFile "docker-compose.yaml"
10. Crie as pastas necessárias ainda usando esse teminal/powershell/cmd
mkdir -p ./dags ./logs ./plugins ./config

<!---
Abrir o docker-compose.yaml e explicar para os alunos o que tem nele, os serviços/volumes/portas e porque tem que criar o .env para este caso específico
-->

11. Criar um arquivo chamado .env na mesma pasta usando o visual studio code e adicionar o seguinte código (sem as aspas)
```
	AIRFLOW_UID=50000
	JWT_SECRET_KEY=7dccbd321d1299e7663d07bbded2f4f1da8f4978c1eaf5ff781326d6005ebcf5
```
12. Executar no terminal o docker compose para subir a aplicação
docker compose up airflow-init 
13. Acesse no navegador o endereço abaixo e entre com usuário e senha airflow e verifique se ocorreu tudo bem
localhost:8080
14. No docker-compose.yaml, abaixo do service postgres adicione o service do PGAdmin
pgadmin:
    container_name: pgadmin4_container
    image: dpage/pgadmin4
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: root
    ports:
      - "5050:80"

<!---
Explicar para os alunos porque não é obrigatório excluir o container existente e subir um novo (adicionamos coisas, quando é opcional)
-->

15. Delete o compose anterior e suba novamente usando o comando no terminal
docker compose down
docker compose up
16. Acesse o banco de dados pelo navegador utilizando a url abaixo: [usuario: admin@admin.com] [senha: root]
localhost:5050
17. Pegue o ip do servidor postgres rodando os comandos abaixo no terminal
(depois de executar o [docker container ls] copie o hash/id da imagem com o nome postgres13 e cole no [docker inspect <cole aqui o hash/id>])
docker container ls
docker inspect <postgres13 container_id>
18. Adicione um novo server clicando em Add new server (vai estar no meio da tela), preencha com os dados abaixo
nome: ps_db
connections: (aba connections)
	username: airflow
	password: airflow
	hostname: o ip coletado
19. cria o database indo em databases > botão direito > create > database e coloque o nome amazon_books
20. visualize em airflow - schemes - tables
21. Volte no navegador, no airflow (localhost:8080) e adicione a conexão com o banco, para isso vai em admin > connections > add connection
22. Insira os dados abaixo e clique em ok.
	connection id: books_connection
	connection type: postgres
	host: o ip anotado
	database: amazon_books
	login: airflow
	password: airflow
	port: 5432