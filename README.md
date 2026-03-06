## TimeGuard

TimeGuard é um sistema de **gerenciamento de tempo por tarefas**, pensado para registrar sessões de trabalho, consolidar duração por atividade e servir como base para uma futura plataforma de produtividade (relatórios, dashboard e interface web).

O backend é construído em **Python + FastAPI + SQLAlchemy**, usando **SQLite** como banco atual e já preparado para migração futura para **PostgreSQL**.

---

## Visão Geral

- **Domínio principal**: controle de tempo por tarefa (timer start/stop).
- **Camadas**:
  - **HTTP / Router**: FastAPI (controllers).
  - **Serviços**: regras de negócio (ex.: “uma sessão aberta por tarefa”).
  - **Acesso a dados**: SQLAlchemy ORM.
  - **Banco de dados**: SQLite (`timeguard.db`) hoje, PostgreSQL no roadmap.
- **Objetivo educacional**: demonstrar boas práticas de backend (camadas, validação, transações, testes futuros).

---

## Tecnologias

- **Linguagem**: Python
- **Framework Web**: FastAPI
- **ORM**: SQLAlchemy
- **Validação / Schemas**: Pydantic
- **Servidor ASGI**: Uvicorn
- **Banco de dados atual**: SQLite
- **Banco de dados futuro (planejado)**: PostgreSQL

---

## Estrutura do Projeto

```text
TimeGuard/
│
├── timeguard.db              # Banco SQLite local
├── app/
│   ├── main.py               # Criação da aplicação FastAPI e registro de rotas
│   ├── core/
│   │   └── config.py         # Configurações (ex.: DATABASE_URL via .env)
│   ├── db/
│   │   └── session.py        # Engine SQLAlchemy e SessionLocal
│   ├── models.py             # Modelos ORM (User, Task, TimeEntry)
│   ├── schemas/              # Schemas Pydantic (TaskCreate, TaskOut, TimeEntryOut)
│   │   └── __init__.py
│   ├── services/
│   │   └── timer_service.py  # Regras de negócio do timer
│   └── routers/              # Rotas / Controllers
│       ├── tasks.py          # Endpoints de tarefas
│       └── timer.py          # Endpoints de timer
│
├── scripts/                  # Scripts auxiliares (criação/seed de banco, testes manuais)
│   ├── create_db.py
│   ├── test_db.py
│   ├── timer_demo.py
│   └── ...
│
├── alembic/                  # Infra de migrations (planejado para uso com PostgreSQL)
└── README.md
```

---

## Modelagem de Dados

### Entidades principais

- **User**
  - `id`
  - `name`
  - `email`
  - `password_hash`
  - `created_at`
  - `updated_at`

- **Task**
  - `id`
  - `user_id` (FK → `users.id`)
  - `title`
  - `description`
  - `status` (`pending`, `in_progress`, `completed`, `canceled`)
  - `priority` (`low`, `medium`, `high`)
  - `due_date`
  - `created_at`
  - `updated_at`

- **TimeEntry**
  - `id`
  - `task_id` (FK → `tasks.id`)
  - `start_time`
  - `end_time` (pode ser `NULL` enquanto a sessão está em aberto)
  - `duration_minutes`
  - `created_at`

### Regra de integridade importante

Para cada tarefa, só pode existir **uma sessão aberta ao mesmo tempo**:

- Não pode haver duas linhas em `time_entries` para a mesma `task_id` com `end_time = NULL`.
- Essa regra hoje é garantida na **camada de serviço** (validação antes de criar nova sessão).
- No futuro, será reforçada no banco (índice parcial único em PostgreSQL).

---

## Arquitetura da API

### Camadas

- **Routers / Controllers (`app/routers`)**
  - Recebem requisições HTTP.
  - Validam entrada com Pydantic (via `schemas`).
  - Chamam serviços de domínio.
  - Padronizam respostas (status code, payload).

- **Serviços (`app/services`)**
  - Implementam as **regras de negócio**:
    - “Pode iniciar timer para esta tarefa?”
    - “Já existe sessão aberta?”
    - “Como calcular `duration_minutes` ao fechar?”

- **Acesso a dados (`app/models.py` + `app/db/session.py`)**
  - Modelos ORM com SQLAlchemy.
  - Engine e `SessionLocal` configurados via `DATABASE_URL`.
  - Uma sessão por requisição (FastAPI dependency injection).

### Schemas (Pydantic)

- `TaskCreate` — dados de entrada para criação de tarefa.
- `TaskOut` — dados de saída da tarefa.
- `TimeEntryOut` — dados de saída das entradas de tempo.
- `TaskWithEntries` — tarefa com lista de entradas de tempo (para futuros relatórios).

---

## Endpoints Principais

### Health Check

- `GET /health`  
  Verifica se a API está respondendo.

- `GET /health-db`  
  Verifica conectividade básica com o banco (executa um `SELECT 1`).

### Tasks

- `POST /tasks`
  - Cria uma nova tarefa.
  - Valida se o `user_id` informado existe.

- `GET /tasks`
  - Lista todas as tarefas cadastradas.

- `GET /tasks/{task_id}`
  - Retorna detalhes de uma tarefa específica.
  - `404` se a tarefa não existir.

### Timer

- `POST /timer/start/{task_id}`
  - Inicia um timer para a tarefa.
  - Cria uma entrada em `time_entries` com `start_time` = agora e `end_time = NULL`.
  - `400` se já houver sessão aberta para essa tarefa.

- `POST /timer/stop/{task_id}`
  - Encerra a sessão aberta mais recente da tarefa.
  - Define `end_time` e calcula `duration_minutes` em Python:
    - `duration_minutes = int((end - start).total_seconds() / 60)`
  - `400` se não houver sessão aberta para essa tarefa.

- `GET /timer/entries/{task_id}`
  - Lista as sessões de tempo de uma tarefa, ordenadas do mais recente para o mais antigo.

---

## Como Rodar o Projeto

### 1) Clonar o repositório

```bash
git clone https://github.com/seu-usuario/timeguard.git
cd timeguard
```

### 2) Criar ambiente virtual

```bash
python -m venv .venv
```

Ativar:

- **Windows**

```bash
.venv\Scripts\activate
```

- **Linux / macOS**

```bash
source .venv/bin/activate
```

### 3) Instalar dependências principais

```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
```

Se for usar PostgreSQL no futuro, será necessário também um driver, por exemplo:

```bash
pip install psycopg2-binary
```

### 4) Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com:

```env
DATABASE_URL=sqlite:///./timeguard.db
```

No futuro, para PostgreSQL, o valor será algo como:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/timeguard
```

### 5) Criar/atualizar o banco SQLite

```bash
python scripts/create_db.py
```

### 6) Subir o servidor

```bash
uvicorn app.main:app --reload
```

Servidor disponível em:

```text
http://127.0.0.1:8000
```

Documentação automática (Swagger UI):

```text
http://127.0.0.1:8000/docs
```

---

## Roadmap

### Fase 1 — Banco de Dados

- Modelagem inicial com SQLite (`timeguard.db`).
- Tabelas: `users`, `tasks`, `time_entries`.
- Scripts de criação e testes (`scripts/create_db.py`, `scripts/test_db.py`, `scripts/timer_demo.py`).

### Fase 2 — API + Regras de Negócio (fase atual)

- Expor o banco via API REST (FastAPI).
- Endpoints para:
  - `Tasks` (CRUD básico).
  - `Timer` (start/stop/list).
- Centralizar regras de negócio no backend.
- Padronizar acesso ao banco com SQLAlchemy.

### Fase 3 — Autenticação

- Implementar autenticação de usuários (por exemplo, JWT).
- Associar tarefas e sessões de tempo a usuários autenticados.
- Restringir acesso aos dados por usuário.

### Fase 4 — Relatórios e Dashboard

- Relatórios de:
  - tempo por tarefa.
  - tempo por dia/semana.
- Endpoints dedicados para consumo por frontend.

### Fase 5 — Migração para PostgreSQL

- Trocar `DATABASE_URL` de SQLite para PostgreSQL.
- Configurar Alembic com `Base.metadata` para gerar e aplicar migrations.
- (Opcional) Migrar dados históricos do `timeguard.db` para PostgreSQL.
- Reforçar regra de “1 sessão aberta por tarefa” com índice parcial único em `time_entries`:
  - `WHERE end_time IS NULL`.

### Fase 6 — Interface Web

- Desenvolver frontend (ex.: React ou Vue).
- Tela de controle de timer (start/stop) em tempo real.
- Dashboard com gráficos e histórico de atividades.

---

## Objetivo do Projeto

Além de resolver um problema real de controle de tempo, o TimeGuard também serve como **projeto de portfólio backend**, demonstrando:

- Modelagem e versionamento de banco de dados.
- Design e implementação de APIs REST com FastAPI.
- Aplicação de regras de negócio em camadas de serviço.
- Uso de SQLAlchemy para abstração de acesso a dados.
- Organização de código, documentação e roadmap evolutivo.

# TimeGuard

TimeGuard é um sistema de **gerenciamento de tempo por tarefas**, projetado para registrar sessões de trabalho e calcular automaticamente o tempo gasto em cada atividade.

O objetivo do projeto é evoluir de um **sistema simples de controle de tempo** para uma **plataforma completa de produtividade**, com API, relatórios e interface web.

---

# Tecnologias Utilizadas

* Python
* SQLite (banco atual)
* PostgreSQL (planejado para próximas fases)
* FastAPI
* SQLAlchemy
* Pydantic
* Uvicorn

---

# Estrutura do Projeto

```
TimeGuard/
│
├── timeguard.db
├── app/
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   └── routers/
│        ├── tasks.py
│        └── timer.py
│
└── README.md
```

---

# Fase 1 — Estrutura do Banco de Dados

Na primeira fase do projeto foi implementado o **modelo de dados do sistema** utilizando SQLite.

## Tabelas principais

### Tasks

Armazena as tarefas que serão monitoradas.

Campos principais:

* `id`
* `title`
* `description`

### Time Entries

Registra sessões de tempo associadas a uma tarefa.

Campos:

* `id`
* `task_id`
* `start_time`
* `end_time`
* `duration_minutes`

## Regras de Negócio

Uma sessão de tempo segue a seguinte lógica:

* `START`

  * cria uma nova linha em `time_entries`
  * `start_time` recebe o horário atual
  * `end_time` permanece `NULL`

* `STOP`

  * atualiza a sessão aberta
  * define `end_time`
  * calcula `duration_minutes`

### Regra importante

Uma tarefa **não pode possuir mais de uma sessão aberta ao mesmo tempo**.

Isso significa que **não pode existir duas entradas com `end_time = NULL` para a mesma task**.

---

# Fase 2 — API + Integração com Banco

A segunda fase transforma o projeto em um **backend completo**, permitindo que o banco de dados seja acessado através de uma **API REST**.

A API foi construída utilizando **FastAPI**, permitindo integração futura com aplicações web ou mobile.

## Objetivos da Fase 2

* Criar uma API HTTP para manipular tarefas e sessões
* Centralizar regras de negócio no backend
* Padronizar acesso ao banco com SQLAlchemy
* Preparar o projeto para expansão futura

---

# Arquitetura da API

A API segue uma arquitetura em camadas:

## Router (Endpoints)

Responsável por:

* receber requisições HTTP
* validar entrada de dados
* retornar respostas padronizadas

Exemplo de rotas:

```
/tasks
/timer
```

---

## Models (ORM)

Define o mapeamento entre:

```
Python Objects  <->  Tabelas do Banco
```

Usando SQLAlchemy.

Exemplo:

```
Task
TimeEntry
```

---

## Schemas

Utilizando **Pydantic** para:

* validar dados de entrada
* definir formato de resposta da API

Exemplos:

```
TaskCreate
TaskOut
TimeEntryOut
```

---

## Database Layer

Responsável por:

* criar a conexão com SQLite
* gerenciar sessões de banco
* controlar transações

---

# Endpoints da API

## Health Check

Verifica se a API está ativa.

```
GET /health
```

---

## Tasks

Criar nova tarefa

```
POST /tasks
```

Listar tarefas

```
GET /tasks
```

Buscar tarefa por ID

```
GET /tasks/{task_id}
```

---

## Timer

Iniciar sessão de tempo

```
POST /timer/start/{task_id}
```

Parar sessão

```
POST /timer/stop/{task_id}
```

Listar sessões de uma tarefa

```
GET /timer/entries/{task_id}
```

---

# Como Rodar o Projeto

### 1) Clonar repositório

```
git clone https://github.com/seu-usuario/timeguard.git
```

---

### 2) Criar ambiente virtual

```
python -m venv .venv
```

Ativar:

Windows

```
.venv\Scripts\activate
```

---

### 3) Instalar dependências

```
pip install fastapi uvicorn sqlalchemy pydantic
```

---

### 4) Rodar servidor

```
uvicorn app.main:app --reload
```

Servidor disponível em:

```
http://127.0.0.1:8000
```

Documentação automática:

```
http://127.0.0.1:8000/docs
```

---

# Próximas Fases do Projeto

## Fase 3

Autenticação de usuários

* Login
* JWT
* Tasks por usuário

## Fase 4

Dashboard e relatórios

* tempo por tarefa
* tempo por dia
* gráficos de produtividade

## Fase 5 — Migração para PostgreSQL

Nesta fase o objetivo é trocar o backend de dados de **SQLite** para **PostgreSQL**, sem quebrar a API existente.

Planejado:

* alterar apenas a `DATABASE_URL` para apontar para um banco PostgreSQL
* usar Alembic com os modelos SQLAlchemy (`Base.metadata`) para criar e evoluir o schema
* opcionalmente migrar os dados históricos do `timeguard.db` para PostgreSQL com um script de migração
* reforçar a regra de **“1 sessão aberta por tarefa”** com um índice parcial único em `time_entries` (`WHERE end_time IS NULL`)

Enquanto isso, o desenvolvimento continua em cima do SQLite, que é simples para testar localmente e já está integrado à API.

## Fase 6

Interface Web

* frontend em React ou Vue
* controle de timer visual
* histórico de atividades

---

# Objetivo do Projeto

Este projeto também serve como **portfólio de desenvolvimento backend**, demonstrando habilidades em:

* design de API
* modelagem de banco de dados
* arquitetura de backend
* versionamento com Git
* boas práticas de desenvolvimento
