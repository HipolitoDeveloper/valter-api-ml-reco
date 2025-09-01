# 🧠 Valter Reco API

Este serviço é responsável por calcular e disponibilizar a **recorrência de produtos comprados por usuários**, com base em registros históricos de transações. Ele utiliza a técnica de média móvel exponencial ponderada (**EWMA**) para classificar a frequência de uso de cada produto por usuário.

## 🚀 Tecnologias Utilizadas

- [Python 3.11+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Psycopg2](https://www.psycopg.org/)
- [Pandas](https://pandas.pydata.org/)
- PostgreSQL (via Prisma no banco principal do Valter)
- Docker (opcional para deploy ou ambiente isolado)

---

## 📁 Estrutura do Projeto

```
valter_reco_api/
├── app/
│   ├── api/
│   │   └── routes.py         # Rotas públicas da API (ex: /train)
│   ├── core/
│   │   └── settings.py       # Configuração do banco de dados
│   ├── services/
│   │   └── ewma.py           # Lógica de cálculo de EWMA
│   │   └── training.py       # Pipeline principal de treinamento
├── main.py                   # Entrypoint da API FastAPI
├── requirements.txt          # Dependências do projeto
```

---

## ⚙️ Como Rodar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/valter_reco_api.git
cd valter_reco_api
```

### 2. Instale as dependências

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz com a seguinte variável:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/database
```

> Certifique-se de que o valor é compatível com o formato do Psycopg2.

### 4. Execute o servidor

```bash
uvicorn src.main:app --reload
```

A API estará disponível em: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Endpoints

### `POST /train`

Aciona o pipeline de treinamento e recalcula todos os `recurrence_score` no banco:

```bash
curl -X POST http://localhost:8000/train
```

Retorna uma lista de registros atualizados com seus respectivos scores.

---

## 🧠 Sobre o Cálculo

O modelo considera transações com estado:

- `PURCHASED`
- `IN_PANTRY`

Para cada combinação `user_id + product_id`, é calculado:

- `ewma_latest`: Média móvel exponencial do intervalo entre compras
- `ewma_avg`: Média simples dos deltas
- `recurrence_score`: Escore final (pode ser um inverso do EWMA ou outra métrica derivada)
- `states_considered`: Estados observados
- `total_logs`: Quantidade de transações consideradas

Os resultados são persistidos na tabela `product_recurrence_score`.

---

## 🛠️ Tabela Esperada no Banco

```sql
CREATE TABLE product_recurrence_score (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    user_id UUID NOT NULL REFERENCES "user"(id),
    product_id UUID NOT NULL REFERENCES product(id),
    recurrence_score DOUBLE PRECISION NOT NULL,
    ewma_latest DOUBLE PRECISION NOT NULL,
    ewma_avg DOUBLE PRECISION NOT NULL,
    total_logs INTEGER NOT NULL,
    states_considered TEXT[] NOT NULL,
    UNIQUE (user_id, product_id)
);
```

---

## 🧪 Testes

Ainda não foram implementados testes automatizados. Recomenda-se o uso do `pytest` e `httpx` para integração com a API.

---


## 👨‍💻 Autor

Engenharia responsável pelo projeto **Valter**