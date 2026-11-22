# Guia de Compatibilização: Notebook Aula_5.ipynb

Este documento reúne todas as instruções, problemas encontrados, correções aplicadas e configurações necessárias para executar o notebook [Aula_5.ipynb](file:///home/vscode/Alura/llamaIndex_pandas_query/Notebooks/Aula_5.ipynb) no ambiente local do **VS Code** com **LlamaIndex**, **Groq API** e **Gradio**.

---

## 1. Contexto e Problemas Originais

Quando o curso foi elaborado, o ecossistema estava em outro cenário:
1. **Credenciais do Google Colab**: O notebook utilizava `from google.colab import userdata` ou nomes genéricos como `secret_key`. No ambiente local do VS Code, as chaves devem ser lidas a partir de um arquivo `.env`.
2. **Modelo da Groq Descontinuado**: O modelo `llama3-70b-8192` foi retirado de catálogo pela Groq.
3. **Incompatibilidade do `llama-index-experimental`**: Versões recentes de `llama-index-core` (0.12+) removeram o `llama_index.core.query_pipeline` em favor de *Workflows*, mas os parsers de Pandas legados dependem estritamente da estrutura do `QueryPipeline`. Além disso, versões recentes do `mistralai` introduziram quebras de importação (`ImportError: cannot import name 'Mistral' / 'DetailedJobOut'`).

---

## 2. Configuração de Variáveis de Ambiente (`.env`)

Crie ou mantenha o arquivo `.env` na raiz do projeto (`/home/vscode/Alura/llamaIndex_pandas_query/.env`):

```env
GROQ_API_KEY=sua_chave_groq_aqui
```

No código Python do notebook, a leitura é feita com a biblioteca `python-dotenv`:

```python
import os
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get("GROQ_API_KEY")
```

---

## 3. Matriz de Versões Compatíveis no Ambiente Virtual

Para garantir que o `QueryPipeline`, o `PandasQueryEngine`, o `PandasInstructionParser` e o `Gradio` funcionem juntos sem conflitos de dependências:

```bash
# Ativar o ambiente virtual (Linux / macOS)
source .venv/bin/activate

# Instalar as versões compatibilizadas
pip install python-dotenv fpdf pandas
pip install llama-index-core==0.11.23 llama-index==0.11.23
pip install llama-index-experimental==0.4.0 "llama-index-llms-groq<0.3.0"
pip install "gradio<5.0" "gradio-client<1.0"
```

---

## 4. Modelos Ativos na API da Groq

Em vez de `llama3-70b-8192`, utilize um modelo de linguagem atualmente ativo:
- **`openai/gpt-oss-120b`** *(Recomendado para melhor raciocínio e geração de código Pandas)*
- **`openai/gpt-oss-20b`** *(Mais rápido e leve)*
- **`qwen/qwen3.8-27b`**

---

## 5. Principais Células Atualizadas no Notebook

### Célula 2 (Listagem de Modelos Groq)
```python
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

key = os.environ.get("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
dados = response.json()["data"]

df = pd.DataFrame(dados)
df["created"] = pd.to_datetime(df["created"], unit="s").dt.strftime("%Y-%m-%d")
df = df[["id", "owned_by", "context_window", "max_completion_tokens", "active", "created"]]
df = df.sort_values("id").reset_index(drop=True)
df
```

### Célula 13 (Configuração Global do LLM)
```python
import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.groq import Groq

load_dotenv()
key = os.environ.get("GROQ_API_KEY")

Settings.llm = Groq(model='openai/gpt-oss-120b', api_key=key)
```

### Célula 48 (Configuração do LLM no Pipeline)
```python
# Na definição do modelo do pipeline:
llm = Groq(model='openai/gpt-oss-120b', api_key=key)
```

### Célula 76 (Aplicação Gradio Completa)
```python
import os
from dotenv import load_dotenv
from llama_index.llms.groq import Groq
from llama_index.core import PromptTemplate
from llama_index.experimental.query_engine.pandas import PandasInstructionParser
from llama_index.core.query_pipeline import (QueryPipeline as QP, Link, InputComponent)
import gradio as gr
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Carregar credenciais locais
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Modelo ativo
llm = Groq(model="openai/gpt-oss-120b", api_key=api_key)

# ... restante das funções do Gradio (pipeline_consulta, carregar_dados, etc.)
```

---

## 6. Seleção de Kernel no VS Code

Ao abrir o notebook no VS Code:
1. No canto superior direito do notebook, clique em **Select Kernel** (ou **Selecionar Kernel**).
2. Escolha **Python Environments...**.
3. Selecione o interpretador do ambiente do projeto: `.venv/bin/python`.
