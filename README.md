# DLT Health Advisor 📊💡🩺

![DLT Health Advisor](https://img.shields.io/badge/DLT_Health_Advisor-v1.0-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)

O **DLT Health Advisor** é uma aplicação desenvolvida para auxiliar pesquisadores e desenvolvedores a escolherem as melhores soluções de tecnologia de registro distribuído (DLT - Distributed Ledger Technology) para sistemas de saúde. O projeto inclui funcionalidades de recomendação baseadas em modelos de aprendizado de máquina, análises sensíveis e comparações detalhadas de diferentes frameworks DLT, com foco em critérios como segurança, escalabilidade, governança e eficiência energética.

## 🚀 Funcionalidades

- **Autenticação de Usuários**: Sistema de login e registro para que pesquisadores possam salvar e carregar comparações.
- **Recomendação Personalizada de DLTs**: Com base em um questionário que analisa os requisitos de segurança, escalabilidade e governança, o sistema sugere frameworks de DLT adequados.
- **Comparações Avançadas**: Pesquisadores podem visualizar comparações de múltiplos frameworks de DLT utilizando gráficos interativos.
- **API para Integração Externa**: Permite que a recomendação de DLTs seja acessada programaticamente via uma API RESTful.
- **Análises Sensíveis**: Ferramenta para entender como pequenos ajustes nos parâmetros influenciam a recomendação final.
- **Visualização Gráfica**: Gráficos avançados como **Radar Charts** para comparar diferentes frameworks de DLT em múltiplas dimensões, facilitando a análise visual.

## 📚 Relevância Acadêmica

As tecnologias de registro distribuído estão transformando a gestão de dados na saúde, aumentando a segurança, a privacidade e a interoperabilidade dos sistemas de saúde. Este projeto oferece:

- **Um ambiente de pesquisa colaborativa**, onde acadêmicos podem testar diferentes frameworks de DLT.
- **Ferramentas de análise comparativa** para entender melhor as implicações das tecnologias de DLT em grandes volumes de dados e redes heterogêneas.
- **Recomendação baseada em evidências**, utilizando machine learning para garantir a escolha de DLTs mais adequadas para cenários críticos da área de saúde.

### Aplicações:

- Redes de prontuários eletrônicos (EHR) 🏥
- Sistemas de interoperabilidade entre hospitais 🌐
- Redes IoT para monitoramento de saúde em tempo real 📡
- Requisitos de alta privacidade e controle de governança em DLTs 🛡️

## 🛠️ Instalação e Configuração

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/DLT_Health_Advisor.git
cd DLT_Health_Advisor
```

### 2. Criar um Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Para Linux/Mac
# ou
venv\Scripts\activate  # Para Windows
```
### 3. Instalar Dependências
As dependências estão listadas no arquivo requirements.txt. Use o seguinte comando para instalá-las:

```bash
pip install -r requirements.txt
```

Exemplo do requirements.txt:

```bash
streamlit
psycopg2-binary
scikit-learn
matplotlib
flask
```

## 4. Configuração do Banco de Dados PostgreSQL

### 4.1 Criar o banco de dados e tabelas:

Use o seguinte SQL para criar as tabelas no PostgreSQL:

```bash
-- Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

-- Tabela de perguntas do framework
CREATE TABLE IF NOT EXISTS perguntasframework (
    id SERIAL PRIMARY KEY,
    descricao TEXT NOT NULL,
    camada_shermin TEXT,
    caracteristica_algoritmo TEXT,
    impacto TEXT,
    ramificacao_sim INTEGER,
    ramificacao_nao INTEGER
);

-- Tabela de respostas dos usuários
CREATE TABLE IF NOT EXISTS respostasusuarios (
    id SERIAL PRIMARY KEY,
    id_pergunta INTEGER NOT NULL REFERENCES perguntasframework(id),
    resposta VARCHAR(3) NOT NULL,
    id_usuario INTEGER NOT NULL REFERENCES users(id)
);

-- Tabela de frameworks de DLT
CREATE TABLE IF NOT EXISTS dlt_frameworks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    tipo_dlt VARCHAR(100),
    grupo_algoritmo VARCHAR(100),
    algoritmo_consenso VARCHAR(100),
    principais_caracteristicas TEXT,
    security DOUBLE PRECISION,
    scalability DOUBLE PRECISION,
    energy_efficiency DOUBLE PRECISION,
    governance DOUBLE PRECISION,
    latency DOUBLE PRECISION
);

-- Tabela de comparações de usuários
CREATE TABLE IF NOT EXISTS user_comparisons (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    comparison_data JSONB
);
```
### 4.2 Configurar as variáveis de ambiente:
Certifique-se de que as seguintes variáveis de ambiente estão configuradas corretamente:

```bash
export PGDATABASE=your_database_name
export PGUSER=your_postgres_user
export PGPASSWORD=your_postgres_password
export PGHOST=localhost
export PGPORT=5432
```

## 5. Executar o Aplicativo
Execute a aplicação usando o Streamlit:

```bash
streamlit run main.py
```

## 6. Executar a API (opcional)
Se quiser habilitar a API para recomendação programática, execute o seguinte comando:

```bash

python api.py
```

## 🌐 API de Recomendação

### Rota /recommend
Endpoint disponível para fazer requisições POST e obter recomendações de DLT programaticamente.

#### Exemplo de Requisição POST:

```bash
curl -X POST http://localhost:5000/recommend -H "Content-Type: application/json" -d '{"respostas_usuario": [1, 0, 1, 0]}'
```


#### Exemplo de Resposta:
```bash
{
  "dlt_inicial": "Hyperledger",
  "dlt_final": "Corda"
}

```

## 📊 Visualizações

O projeto suporta gráficos avançados como Radar Charts para comparar múltiplos frameworks de DLT em diferentes critérios. Aqui está um exemplo de comparação de segurança, escalabilidade, eficiência energética, governança e latência.

## 🎓 Contribuição Acadêmica

Este projeto foi projetado para a comunidade acadêmica, com o intuito de:

Proporcionar uma plataforma de análise comparativa de diferentes soluções DLT para sistemas de saúde.
Permitir que pesquisadores testem suas hipóteses e estratégias de implementação de DLT com base em dados concretos e recomendações automáticas.
Fomentar a colaboração em redes distribuídas de saúde, onde privacidade, segurança e interoperabilidade são cruciais.
Se você é um pesquisador ou desenvolvedor interessado em DLTs para a saúde, sinta-se à vontade para contribuir ou utilizar este projeto como base para experimentos e trabalhos futuros.

## 🖥️ Estrutura do Projeto
```bash
my_dlt_project/
│
├── main.py               # Arquivo principal que executa a aplicação Streamlit
├── database.py           # Conexão com o banco de dados e funções relacionadas
├── auth.py               # Funções de autenticação (login/registro)
├── recommendation.py     # Lógica de recomendação (baseada em regras e machine learning)
├── user_comparisons.py   # Funções para salvar e carregar comparações do usuário
├── api.py                # API para acessar o motor de recomendação via HTTP
├── visualizations.py     # Gráficos de radar e outras visualizações avançadas
├── decision_tree.py      # Implementação do modelo de árvore de decisão
└── README.md             # Instruções e detalhes sobre o projeto
```

## 📖 Licença

Este projeto está licenciado sob a MIT License. Sinta-se à vontade para usar e modificar o código conforme necessário.

Se você deseja discutir melhorias, reportar problemas ou compartilhar resultados acadêmicos baseados neste projeto, sinta-se à vontade para abrir uma issue ou fazer um pull request.




