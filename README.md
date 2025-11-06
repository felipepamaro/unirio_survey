# API de Pesquisa UNIRIO via Telegram

## 1. Introdução

Este projeto é uma API de back-end construída para conduzir uma pesquisa de satisfação simples via Telegram, especificamente para a comunidade da UNIRIO.



O fluxo de interação de utilização e coleta das respostas funciona conforme a sequência abaixo:

1. Um usuário inicia o bot no Telegram e envia o comando `/iniciar`.
2. A API identifica o usuário pelo seu `chat_id` e inicia uma **nova** pesquisa.
3. O sistema faz a Pergunta 1: `"Qual o seu vínculo principal com a UNIRIO?"`.
4. Após a resposta, o sistema armazena o dado e faz a Pergunta 2: `"Se você fosse o conselheiro do nosso Reitor por um dia, qual sugestão você daria para melhorar a UNIRIO?"`.
5. O sistema armazena a segunda resposta e envia uma mensagem de agradecimento, concluindo a pesquisa.
6. O usuário pode responder novamente a qualquer momento enviando `/iniciar` novamente.
7. Toda vez que o usuário enviar a mensagem `/iniciar` o processo será reiniciado.



### Tecnologias Utilizadas

* **Python 3.8+**: A linguagem de programação principal.
* **FastAPI**: O framework web para construir a API.
* **API de Bots do Telegram**: O serviço que faz a ponte entre nossa API e o app Telegram.
* **SQLAlchemy**: Biblioteca para interagir com o banco de dados.
* **SQLite**: Um banco de dados leve e baseado em arquivo.
* **Uvicorn**: O servidor que "roda" a aplicação FastAPI.
* **Ngrok** : Ferramenta que expõe nosso servidor local para a internet, permitindo que o Telegram se comunique com ele.

---

## 2. Pré-requisitos

Antes de começar, você precisará ter alguns programas e contas configuradas:

1. **Python 3.8 ou superior**:
   * Acesse [python.org](https://www.python.org/downloads/) e baixe o instalador.
   * **Importante para Windows**: Durante a instalação, marque a caixa que diz **"Add Python to PATH"**.
2. **Git**:
   * Necessário para baixar (clonar) o código do repositório.
   * Acesse [git-scm.com](https://git-scm.com/downloads) e baixe o instalador.
3. **Conta no Telegram e um Token de Bot**:
   * Você precisa de uma conta de usuário do Telegram.
   * Dentro do app, procure pelo bot [@BotFather](https://t.me/BotFather) (o bot oficial verificado). 
   * Inicie uma conversa com ele e envie o comando `/newbot`.
   * Siga as instruções para dar um nome (ex: `Pesquisa UNIRIO`) e um nome de usuário (ex: `PesquisaUnirioBot`).
   * Ao final, o BotFather fornecerá um **TOKEN DA API**. Guarde este token, ele é sua chave secreta que será utilizado na API.
4. **Ngrok** (para teste local):
   * Crie uma conta gratuita em [ngrok.com](https://dashboard.ngrok.com/signup).
   * Após criar a conta, siga as instruções do site para baixar o executável.

---

## 3. Guia de Instalação e Execução

Siga estes passos detalhados para rodar o projeto em sua máquina.

### Passo 1: Baixar o Projeto (Clonar)

Abra seu terminal (Prompt de Comando ou PowerShell no Windows, Terminal no Linux/macOS) e execute o comando abaixo para baixar os arquivos do projeto.

Bash

```
git clone https://github.com/felipepamaro/unirio_survey
cd unirio_survey
```

### Passo 2: Criar um Ambiente Virtual (Venv)

É uma boa prática isolar as dependências do projeto. Vamos criar um "ambiente virtual" (uma pasta chamada `venv`) para isso.

**No Windows (Prompt de Comando / PowerShell):**

Bash

```
# 1. Cria o ambiente virtual

python -m venv venv

# 2. Ativa o ambiente virtual

.\venv\Scripts\activate
```

**No Linux ou macOS:**

Bash

```
# 1. Cria o ambiente virtual

python3 -m venv venv

# 2. Ativa o ambiente virtual

source venv/bin/activate
```

> **Dica:** Após ativar, você verá `(venv)` aparecer no início do seu prompt, indicando que o ambiente está ativo.

### Passo 3: Instalar as Dependências

Com o ambiente virtual ativo, instale todas as bibliotecas que o projeto precisa de uma só vez, usando o arquivo `requirements.txt`.

Bash

```
pip install -r requirements.txt
```

### Passo 4: Configurar as Variáveis de Ambiente

Este é o passo mais importante. Precisamos informar ao projeto suas chaves secretas do Twilio sem colocá-las diretamente no código.

1. Na pasta raiz do projeto, crie um arquivo chamado exatamente `.env` (sem nada antes do ponto).

2. Abra este arquivo com um editor de texto (como Bloco de Notas, VS Code, etc.).

3. Copie e cole o conteúdo abaixo, substituindo os valores `<SEU_TOKEN>` pelo chave que foi gerado pelo [@BotFather](https://t.me/BotFather).

**Arquivo: `.env`**

```
TELEGRAM_BOT_TOKEN=<SEU_TOKEN>
```

Agora está tudo pronto para iniciar o servidor. No mesmo terminal onde você ativou o `venv`, execute:

Bash

```
uvicorn main:app --reload
```

- `uvicorn`: O servidor.

- `main:app`: Diz ao servidor para procurar no arquivo `main.py` a variável `app`.

- `--reload`: Faz o servidor reiniciar automaticamente se você alterar algum arquivo de código (ótimo para desenvolvimento).

Se tudo der certo, você verá uma saída parecida com esta:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [37841] using WatchFiles
INFO:     Started server process [37843]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Passo 6: Testar o Servidor (Health Check)

Com o servidor rodando, abra seu navegador de internet e acesse [http://127.0.0.1:8000/](https://www.google.com/search?q=http://127.0.0.1:8000/&authuser=2).

Você deve ver a seguinte resposta em JSON, confirmando que a API está no ar:

JSON

```
{"status":"live"}
```

---

## 4. Conectando o Telegram com sua API (Ngrok)

Nossa API está rodando apenas na sua máquina (`localhost:8000`). O telegram, que está na internet, não consegue acessá-la. Precisamos criar um "túnel" público seja possível fazer API encontrar o seu código.

### Passo 7: Iniciar o Ngrok

1. Abra um **NOVO** terminal (mantenha o terminal do Uvicorn rodando!).

2. Navegue até a pasta onde você baixou o `ngrok`.

3. Execute o ngrok apontando para a porta `8000` (a mesma porta do Uvicorn).

Bash

```
# No Windows

ngrok.exe http 8000



# No Linux/macOS

./ngrok http 8000
```

O Ngrok irá iniciar e mostrar uma tela com várias informações. Procure pela linha `Forwarding` que começa com `https`:

```
Forwarding https://a1b2-c3d4-e5f6.ngrok-free.app -> http://localhost:8000
```

**Copie esta URL `https`**. Esta é a sua URL pública temporária.

### Passo 8: Configurar o Webhook no Telegram (Etapa Única)

Agora, precisamos dizer ao Telegram para onde ele deve enviar as mensagens do seu bot.

1. Pegue o **TOKEN** do seu bot (do `.env`) e a **URL do Ngrok** (do passo 7).

2. Abra seu **navegador de internet**.

3. Monte e cole a seguinte URL na barra de endereços, substituindo os valores:
   
   `https://api.telegram.org/bot<SEU_TOKEN_AQUI>/setWebhook?url=<SUA_URL_NGROK_AQUI>/webhook
   
   **Exemplo:** `https://api.telegram.org/bot123456...efg/setWebhook?url=https://a1b2-c3d4-e5f6.ngrok-free.app/webhook`

4. Pressione Enter. O navegador deve mostrar uma resposta JSON de sucesso:
   
   JSON
   
   ```
   {"ok":true,"result":true,"description":"Webhook was set"}
   ```

**Pronto!** Seu bot do Telegram está oficialmente conectado à sua API FastAPI.



### Passo 9: Testar a Pesquisa!

Pronto! Agora você pode testar o fluxo completo:

1. Certifique-se de que seu servidor (`uvicorn`) está rodando.

2. Certifique-se de que o `ngrok` está rodando.

3. Pegue seu celular e envie qualquer mensagem para o seu bot com a mensagem `/iniciar` para começar a nova pesquisa.

O bot deverá responder com a primeira pergunta, e a pesquisa começará. As respostas serão salvas em um arquivo chamado `survey.db` na pasta do seu projeto.




