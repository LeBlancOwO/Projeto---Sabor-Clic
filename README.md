&lt;div align=&quot;center&quot;&gt;

# 🍬 Sabor&Clic · Doce Celebração

### *Doces feitos com amor, a um clique de você.*

Site de uma doceria com cardápio, cadastro, login, pedidos, painel de cozinha, administração e contratação de serviços de buffet.







[Sobre](#-sobre-o-projeto) · [Funcionalidades](#-funcionalidades) · [Identidade visual](#-identidade-visual) · [Como executar](#-como-baixar-e-executar) · [Rotas](#-rotas-e-perfis-de-acesso) · [Estrutura](#-estrutura-do-projeto) · [Problemas comuns](#-problemas-comuns)

&lt;/div&gt;

---

## 🍰 Sobre o projeto

A **Doce Celebração** apresenta doces, bolos, sobremesas e serviços de buffet para aniversários, festas e outras ocasiões especiais. O site tem visual delicado e responsivo, com atendimento pelo WhatsApp, e utiliza **Flask** com banco de dados **SQLite** (`banco.db`) criado automaticamente na primeira execução.

&lt;!-- Adicione um print do site: crie a pasta docs/ e coloque a imagem lá --&gt;
&lt;!--  --&gt;

---

## ✨ Funcionalidades

- 🏠 **Página inicial** com banners, benefícios e categorias
- 🧁 **Cardápio** com lista de produtos, estoque e busca
- 🛒 **Carrinho e pedidos** com acompanhamento de status
- 🎉 **Serviços de buffet** com agendamento e reserva
- 🔐 **Cadastro e login** com controle por perfil (`cliente`, `cozinheiro` e `administrador`)
- 👩‍🍳 **Painel da cozinha** (`/cozinha`) para gerenciamento de preparo
- ⚙️ **Painel administrativo** (`/admin`) para gestão de usuários, cardápio e reservas
- 📱 **Layout responsivo** (computador, tablet e celular) + botão flutuante de WhatsApp

---

&lt;div align=&quot;center&quot;&gt;

## 🎨 Identidade visual

| Cor | Código | Uso |
|---|---|---|
|  Rosa-claro | `#F8DADD` | Fundos suaves e botões |
|  Rosa | `#E98C9C` | Destaques e faixa de benefícios |
|  Rosa antigo | `#C96D7D` | Hover dos botões |
|  Marrom | `#795044` | Textos e rodapé |
|  Vinho | `#A83F50` | Títulos e botões principais |

**Tipografia:** `Playfair Display` · `Dancing Script` · `Poppins`

&lt;/div&gt;

---

## 🚀 Como baixar e executar

### Requisitos

- [Python 3.10 ou superior](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads) *(opcional, caso baixe via ZIP)*

### 1. Baixar o projeto

```bash
git clone <LINK-DO-SEU-REPOSITORIO>
cd Projeto---Sabor-Clic
```

> [!TIP]
> Se você baixou pelo botão **Code › Download ZIP** no GitHub, extraia o arquivo e abra o terminal dentro da pasta `Projeto---Sabor-Clic-main` (onde está o arquivo `run.py`).

### 2. Criar e ativar o ambiente virtual

&lt;details&gt;
&lt;summary&gt;&lt;b&gt;🐧 Linux / macOS&lt;/b&gt;&lt;/summary&gt;

```bash
python3 -m venv .venv
source .venv/bin/activate
```
&lt;/details&gt;

&lt;details&gt;
&lt;summary&gt;&lt;b&gt;🪟 Windows (PowerShell)&lt;/b&gt;&lt;/summary&gt;

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
&lt;/details&gt;

Quando o ambiente estiver ativo, `(.venv)` aparecerá no início da linha do terminal.

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

> [!WARNING]
> Caso o `pip` retorne erro de decodificação ao ler o `requirements.txt` (por estar salvo em UTF-16 LE), instale os pacotes principais diretamente:
>
> ```bash
> pip install Flask bcrypt
> ```

### 4. Executar a aplicação

Na **pasta raiz do projeto** (onde fica o `run.py`), execute:

```bash
python run.py
```

*(No Linux/macOS, use `python3 run.py` caso o comando `python` não esteja mapeado.)*

### 5. Acessar no navegador

&lt;div align=&quot;center&quot;&gt;

```text
http://127.0.0.1:5000
```

&lt;/div&gt;

Para encerrar o servidor, pressione `Ctrl + C` no terminal.

> [!IMPORTANT]
> **Primeiro acesso (Administrador):** na primeira execução, o sistema cria automaticamente o banco `banco.db` e um usuário `admin` (`admin@docecelebracao.com`) com uma senha aleatória exibida no terminal:
> `[SETUP] Admin criado. Usuário: admin | Senha gerada: ...`
>
> Caso perca a senha, execute `python resetar_admin.py` na raiz do projeto para definir uma nova.

---

&lt;div align=&quot;center&quot;&gt;

## 🔐 Rotas e perfis de acesso

| Rota | Descrição | Acesso necessário |
|---|---|---|
| `/` | Página inicial | Público |
| `/cardapio` | Cardápio de doces e produtos | Público |
| `/cadastro` | Cadastro de novos usuários | Público |
| `/login` | Autenticação no sistema | Público |
| `/carrinho` | Carrinho de compras e pedidos | Usuário logado |
| `/servicos` | Reserva de serviços de buffet | Usuário logado |
| `/cozinha` | Painel da cozinha | `cozinheiro` ou `administrador` |
| `/admin` | Painel administrativo | `administrador` |

### ⚙️ Variáveis de ambiente (opcional)

| Variável | Descrição |
|---|---|
| `FLASK_DEBUG=1` | Ativa o modo de depuração do Flask |
| `ADMIN_SENHA` | Define uma senha fixa para o usuário `admin` na criação inicial do banco |
| `SECRET_KEY` | Mantém as sessões ativas mesmo após reiniciar o servidor |
| `COOKIE_SECURE=1` | Marca o cookie de sessão como `Secure` (usar apenas em produção com HTTPS) |
| `EMAIL_REMETENTE` e `SENHA_APP_GMAIL` | Credenciais SMTP para envio real de e-mails de cancelamento (sem elas, o envio é apenas simulado no terminal) |

&lt;/div&gt;

---

## 📁 Estrutura do projeto

```text
Projeto---Sabor-Clic-main/
├── app/
│   ├── controllers/   # Rotas e regras de controle (auth, cardápio, carrinho, cozinha, buffet, admin, etc.)
│   ├── models/        # Conexão SQLite e modelos do banco de dados
│   ├── static/        # Arquivos CSS, JavaScript e imagens
│   ├── utils/         # Serviço de envio/simulação de e-mails
│   ├── views/         # Templates HTML (Jinja2)
│   └── __init__.py    # Factory da aplicação Flask, blueprints e triggers do banco
├── requirements.txt   # Dependências do projeto
├── resetar_admin.py   # Script para redefinir a senha do usuário admin
├── run.py             # Ponto de entrada para iniciar o servidor
├── LICENSE
└── README.md
```

---

## 🛠️ Problemas comuns

&lt;details&gt;
&lt;summary&gt;&lt;code&gt;No module named &#39;flask&#39;&lt;/code&gt; ou &lt;code&gt;No module named &#39;bcrypt&#39;&lt;/code&gt;&lt;/summary&gt;

O ambiente virtual não está ativo ou as dependências não foram instaladas. Repita os passos 2 e 3.
&lt;/details&gt;

&lt;details&gt;
&lt;summary&gt;Erro de encoding/Unicode ao rodar &lt;code&gt;pip install -r requirements.txt&lt;/code&gt;&lt;/summary&gt;

O arquivo `requirements.txt` original está em UTF-16 LE. Instale manualmente com `pip install Flask bcrypt` ou converta o arquivo para UTF-8.
&lt;/details&gt;

&lt;details&gt;
&lt;summary&gt;&lt;code&gt;No such file or directory&lt;/code&gt; ao rodar &lt;code&gt;python run.py&lt;/code&gt;&lt;/summary&gt;

Confira se você está na pasta raiz do projeto (onde ficam `run.py` e a pasta `app/`) antes de rodar `python run.py`. No Linux, maiúsculas e minúsculas importam.
&lt;/details&gt;

&lt;details&gt;
&lt;summary&gt;O site abre sem estilo (CSS)&lt;/summary&gt;

Recarregue com `Ctrl + Shift + R` para limpar o cache do navegador e confira se os arquivos estão em `app/static/css/` e `app/static/js/`.
&lt;/details&gt;

---

&lt;div align=&quot;center&quot;&gt;

## 👩‍💻 Autores

- [Gabriela de Paula Silvestre Correa](https://www.google.com/search?q=https://github.com/EuGranola)
- [Gabrielle Pereira do Amaral]((https://github.com/LeBlancOwO))
- [Grazielly Seixas Gaspar] ()
- [Matheus Consani Mercom França] ()

---

🍬 **Sabor&Clic · Doce Celebração** — *Feito com amor e açúcar*

&lt;/div&gt;
