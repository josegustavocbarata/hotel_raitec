# 🏨 Hotel Raitec

Sistema de gerenciamento de hotel em Python, com menu interativo, organizado em camadas (models, repository, controllers e ui). Permite cadastrar quartos e clientes, criar reservas e controlar o fluxo de check-in e check-out.

<!-- TODO: adicione 1 ou 2 frases sobre o contexto do projeto (disciplina, cliente, objetivo) -->

## Funcionalidades

- **Autenticação de acesso** antes de usar o sistema
- **Cadastro de quartos** (número, tipo, valor e status de ocupação)
- **Cadastro de clientes** (nome, idade e CPF)
- **Reservas** de um quarto para um cliente, com data de entrada e de saída
- **Check-in** e **check-out** a partir do ID da reserva (o check-out libera o quarto e remove a reserva)
- **Listagens** de clientes e reservas cadastrados

## Estrutura do projeto

```
hotel_raitec/
├── controllers/     # Regras de negócio (HotelController)
├── models/          # Entidades: Client, Room, Booking
├── repository/      # Acesso e persistência dos dados
├── ui/              # Interface de menu (ui/menu.py)
├── ca.pem           # Certificado CA para conexão segura
├── main.py          # Ponto de entrada
├── teste.py         # Script de teste do fluxo completo
└── .gitignore
```

### Arquitetura

| Camada | Responsabilidade |
| --- | --- |
| `ui` | Exibe o menu e recebe a entrada do usuário; chama o controller |
| `controllers` | Aplica as regras de negócio (autenticação, reservas, check-in/out) |
| `models` | Define as entidades do domínio |
| `repository` | Lê e grava os dados |

### Modelos

| Modelo | Atributos |
| --- | --- |
| `Client` | nome, idade, CPF |
| `Room` | número, tipo, valor, ocupado |
| `Booking` | cliente, quarto, data de entrada, data de saída |

## Como executar

### Pré-requisitos

- Python 3.8 ou superior
<!-- TODO: liste as dependências (ex.: mysql-connector-python, python-dotenv) e, se houver, crie um requirements.txt -->
<!-- TODO: descreva a configuração do banco de dados / variáveis de ambiente, se existirem -->

### Instalação

```bash
git clone https://github.com/josegustavocbarata/hotel_raitec.git
cd hotel_raitec
pip install -r requirements.txt
```

### Execução

```bash
python main.py
```

O `main.py` chama `ui.menu.start()`, que abre o menu principal do sistema.

## Testes

O arquivo `teste.py` executa o fluxo completo diretamente no `HotelController`:

1. Autenticação
2. Registro de 3 quartos (Simples, Duplo e Luxo)
3. Registro de 20 clientes fictícios
4. Criação de uma reserva
5. Listagem de clientes
6. Check-in e check-out

```bash
python teste.py
```

> ⚠️ O script grava dados de exemplo (quartos, clientes e reservas). Rode-o em um ambiente de desenvolvimento, não em dados reais.

## Segurança

- Não versione senhas, tokens ou arquivos `.env`; mantenha-os no `.gitignore`.

## Autor

**José Gustavo C. Barata**: [@josegustavocbarata](https://github.com/josegustavocbarata)
