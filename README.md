# Sabor&Clic – Doce Celebração

Site de uma doceria com cardápio, cadastro, login, pedidos e contratação de serviços de buffet. Desenvolvido com **Python (Flask)**, **HTML**, **CSS** e **JavaScript**.

## Requisitos

- [Python 3.10 ou superior](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## Como baixar e executar

### 1. Baixar o projeto

```bash
git clone <LINK-DO-SEU-REPOSITORIO>
cd Projeto---Sabor-Clic
```

Você também pode baixar o ZIP pelo botão verde **Code > Download ZIP** aqui no GitHub e extrair a pasta.

### 2. Criar o ambiente virtual

**Linux / macOS**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Quando o ambiente estiver ativo, aparece `(.venv)` no começo da linha do terminal.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar o programa

```bash
cd SaborEClic_PY
python run.py
```

### 5. Abrir no navegador

Acesse o endereço que aparecer no terminal, normalmente:

```
http://127.0.0.1:5000
```

Para parar o servidor, aperte `Ctrl + C` no terminal.



## Problemas comuns

- **`No module named 'flask'`**: o ambiente virtual não está ativo ou as dependências não foram instaladas. Repita os passos 2 e 3.
- **O site abre sem estilo (CSS)**: recarregue com `Ctrl + Shift + R` para limpar o cache do navegador.
- **`No such file or directory`**: confira se você está na pasta `SaborEClic_PY` antes de rodar `python run.py`. No Linux, maiúsculas e minúsculas importam.
