# GlobalSIM — Serviço Internacional de Internet por eSIM (EDII)

Projeto prático da disciplina **Estruturas de Dados II** (Sistemas de Informação — UNEB, Profra. Maria Inés Restovic).

---

## Integrantes da Equipe
- Marcelo Líryo, Janderson Blanki

---

## Etapa 1: Tabela Hash e Aplicação Web

### 1. Estrutura Implementada (`HashTable`)
A classe `HashTable` (`app/models/hash_table.py`) foi implementada do zero utilizando **encadeamento externo (*separate chaining*)** para tratamento de colisões:
- **Chave**: Código internacional do país de 2 ou 3 letras normalizado em maiúsculas (`BR`, `PT`, `ES`, `FR`, `IT`, `US`, `CA`, `JP`).
- **Função de Espalhamento (`_hash_function`)**: Polinomial com base prima (`37`) ponderada pela posição do caractere, distribuindo chaves curtas de forma uniforme entre os *buckets*.
- **Instrumentação**: O sistema monitora e exibe na interface Web:
  - Capacidade da tabela ($M$), total de elementos ($N$) e Fator de Carga ($\alpha = N / M$).
  - Quantidade de *buckets* ocupados, colisões ativas e número de comparações na última busca.
  - Visualização gráfica de cada *bucket* e das listas encadeadas formadas em caso de colisão.

### 2. Arquitetura em Camadas e Persistência
- **`app/repository/country_repository.py`**: Único módulo que manipula o arquivo `app/data/countries.json` (usando `pathlib.Path` para compatibilidade entre Windows e Linux) e prepara exportação para `pandas.DataFrame`.
- **`app/models/country.py`**: Camada de negócio (`CountryModel`) que mantém a `HashTable` em memória durante a execução e aciona o repositório para persistir alterações.
- **`app/routes/home.py` e `app/routes/admin.py`**: Rotas Flask com templates Jinja2, formulários HTML e padrão **Post/Redirect/Get (PRG)**.

---

## Diferencial da Equipe: Recomendação de Pacote de Dados a partir do Roteiro de Viagem

### Problema Resolvido
Viajantes internacionais frequentemente visitam múltiplos países em uma única viagem e precisam saber rapidamente se todos os destinos possuem cobertura eSIM e qual pacote de dados oferece a melhor relação de franquia e cobertura regional.

### Integração por Etapas
1. **Etapa 1 (Tabela Hash)**: O viajante informa a sequência de países do seu roteiro (ex.: `PT, ES, FR, IT`). O sistema realiza buscas sucessivas em tempo médio $O(1)$ na `HashTable`, contabiliza o total de comparações, separa destinos cobertos/não cobertos e analisa o conjunto de regiões atendidas para recomendar automaticamente entre os pacotes `Europa Basic (101)`, `Europa Plus (102)`, `América Basic (201)`, `América Plus (202)` ou `Global (301)`.
2. **Etapa 2 (Árvore B)**: Permitirá associar diretamente o pacote recomendado pelo roteiro ao cadastro do cliente e seu respectivo `eSIM` armazenados na Árvore B.
3. **Etapa 3 (Grafos)**: Integrará o roteiro de múltiplos destinos ao Grafo ponderado da rede internacional para calcular a latência acumulada entre os países da viagem via algoritmo de Dijkstra.

---

## Como Executar o Projeto (Windows e Linux)

### 1. Criar e ativar o ambiente virtual (`venv`)

**No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**No Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 2. Instalar as dependências
```bash
pip install -r requirements.txt
```

### 3. Executar a aplicação Flask
```bash
python run.py
```

Acesse no navegador:
- Página Inicial / Consulta de Cobertura / Roteiro: http://127.0.0.1:5000/
- Painel Administrativo / Instrumentação da Tabela Hash: http://127.0.0.1:5000/admin/

### 4. Executar os Testes Automatizados
```bash
pytest -v
```
