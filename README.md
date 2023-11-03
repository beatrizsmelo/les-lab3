# Tabela de conteúdos
  1. [Gerando Personal Access Token](#gerando-personal-access-token)
  2. [Armazenando variáveis de ambiente](#armazenando-variáveis-de-ambiente)
  3. [Instalando as dependências do projeto](#instalando-as-dependências-do-projeto)
  4. [Executando o projeto](#executando-o-projeto)

  ---

# Gerando Personal Access Token

  1. Acesse seus **tokens pessoais** cadastrados no [Github](https://github.com/settings/tokens)
  2. Crie um novo **token pessoal** com **todas** as permissões definidas
  3. Copie o novo **token pessoal** gerado
  4. Repita o procedimento, resultando ao todo em **dois novos tokens**

# Armazenando variáveis de ambiente

  1. Na raiz do projeto, crie um novo arquivo chamado **.env**
  2. Esse arquivo deve conter duas chaves, **ACCESS_TOKEN1** e **ACCESS_TOKEN2**
  3. Cada chave deve conter, entre aspas duplas, um dos **tokens pessoais** gerados anteriormente:

  ```
  ACCESS_TOKEN1="um token aqui"
  ACCESS_TOKEN2="outro token aqui"
  ```
  >Há um arquivo **.env.example** no projeto em caso de dúvidas de como deve ser montado seu arquivo **.env**

# Instalando as dependências do projeto

  No terminal, apontado para a raiz do projeto, insira o comando:

  ### Powershell ou Prompt de Comando
  ```
  pip install -r .\requirements.txt
  ```
  ### Git Bash
  ```
  pip install -r ./requirements.txt
  ```

# Executando o projeto

  No terminal, apontado para a raiz do projeto, insira o comando:
  
  ### Powershell ou Prompt de Comando
  ```
  python .\src\main.py
  ```
  ### Git Bash
  ```
  python ./src/main.py
  ```