from controllers.hotel_controller import HotelController
from models.client import Client
from models.room import Room
from models.booking import Booking
from datetime import datetime

controller = HotelController()
_booking_counter = 1  # Auto-incremento de IDs de reserva



#gerais
def input_validado(prompt: str, conversor, msg_erro: str):
    while True:
        raw = input(f"  {prompt}").strip()
        try:
            return conversor(raw)
        except (ValueError, TypeError):
            print(f"  {msg_erro}")

def input_int(prompt: str) -> int:
    return input_validado(prompt, int, "Digite um número inteiro válido.")

def input_float(prompt: str) -> float:
    return input_validado(prompt, float, "Digite um valor numérico válido.")

def input_date(prompt: str) -> datetime:
    return input_validado(
        f"{prompt} (dd/mm/aaaa): ", 
        lambda d: datetime.strptime(d, "%d/%m/%Y"), 
        "Data inválida. Use o formato dd/mm/aaaa."
    )

def pause():
    #tempo de leitura no menu
    input("\n  [Enter para continuar]")


def fmt_date(d: datetime) -> str:
    #formata as datas pra string
    return d.strftime("%d/%m/%Y")


def fmt_booking(b: dict) -> str:
    status = "✔ Check-in realizado" if b.get('active') else "⏳ Aguardando"
    
    checkin = b.get('checkin')
    checkout = b.get('checkout')
    checkin_str = checkin.strftime("%d/%m/%Y") if checkin else "?"
    checkout_str = checkout.strftime("%d/%m/%Y") if checkout else "?"
    
    return (
        f"  ID: {b.get('id')} | "
        f"Cliente: {b.get('client_name', b.get('client_cpf'))} | "
        f"Quarto: {b.get('room_number')} | "
        f"Entrada: {checkin_str} | "
        f"Saída: {checkout_str} | "
        f"Status: {status}"
        f"Valor Total: {b.get('total_expense')}"
    )

def fmt_room(r: dict) -> str:

    status = "Ocupado" if r.get('occupied') else "Livre"

    return (
        f"  Nº {r.get('number')} | "
        f"Máx. pessoas: {r.get('max_people') } | "
        f"Diária: R$ {r.get('daily_price'):.2f} | " 
        f"Status: {status}"
    )

#menu geral
def start():
    while True:
        print("HOTEL SYS")
        print("1 · Área do Cliente")
        print("2 · Administração")
        print("0 · Sair")
        opt = input("  Escolha: ").strip()

        match opt:
            case "1": menu_cliente()
            case "2": menu_admin_login()
            case "0":
                print("\n  Encerrando sistema. Até logo!\n")
                exit()
            case _: print("  Opção inválida.")

#menu cliente
def menu_cliente():
    while True:
        print("\nÁREA DO CLIENTE ")
        print("  1 · Criar conta")
        print("  2 · Entrar (login por CPF)")
        print("  0 · Voltar")
        opt = input("  Escolha: ").strip()

        match opt:
            case "1": cadastrar_cliente()
            case "2": login_cliente()
            case "0": break
            case _: print("  Opção inválida.")

#cadastrar cliente ou achar existente
def cadastrar_cliente():
    print("\n  Criar Conta")
    nome = input("  Nome completo: ").strip()
    if not nome:
        print("  Erro: o nome não pode estar vazio.")
        return
    idade = input_int("Idade: ")
    cpf = input("  CPF: ").strip()
    if not cpf:
        print("  Erro: o CPF não pode estar vazio.")
        return

    cliente = Client(nome, idade, cpf)
    controller.register_client(cliente)
    pause()


def login_cliente():
    print("\n  Login")
    cpf = input("  CPF: ").strip().replace(".", "").replace("-", "")
    cliente = controller.get_all_clients().get(cpf)

    if cliente:
        print(f"\n  Bem-vindo(a), {cliente.get('name')}!")
        menu_cliente_logado(cliente)
    else:
        print("  CPF não encontrado. Cadastre-se primeiro.")
        pause()


#menu cliente logado
def menu_cliente_logado(cliente: Client):
    #menu geral do cliente
    while True:
        print(f"\nOLÁ, {cliente.get('name').upper()}")
        print("  1 · Minhas reservas")
        print("  2 · Solicitar reserva")
        print("  3 · Cancelar reserva")
        print("  4 · Ver quartos disponíveis")
        print("  0 · Sair da conta")
        opt = input("  Escolha: ").strip()

        match opt:
            case "1": ver_reservas_cliente(cliente)
            case "2": solicitar_reserva(cliente)
            case "3": cancelar_reserva_cliente(cliente)
            case "4": listar_quartos_disponiveis()
            case "0": break
            case _: print("  Opção inválida.")


def ver_reservas_cliente(cliente: Client):
    #mostra as reservas do cliente já logado
    print(f"\n   Reservas de {cliente.get('name')}") # type: ignore
    reservas = [
        b for b in controller.get_all_bookings().values()
        if b.get('client_cpf') == cliente.get('cpf') # type: ignore
    ]
    if not reservas:
        print("  Nenhuma reserva encontrada.")
    else:
        for b in reservas:
            print(fmt_booking(b))
    pause()


def listar_quartos_disponiveis():
    #mostra quartos disponiveis no hotel
    print("\n Quartos Disponíveis")
    disponiveis = [r for r in controller.get_all_rooms().values() if not r.get('occupied')]
    if not disponiveis:
        print("  Nenhum quarto disponível no momento.")
    else:
        for q in disponiveis:
            print(fmt_room(q))
    pause()


def solicitar_reserva(cliente: Client):
    print("\nSolicitar Reserva")

    #mostra de novo os quartos disponíveis antes de pedir a escolha
    disponiveis = [r for r in controller.get_all_rooms().values() if not r.get('occupied')] # type: ignore
    if not disponiveis:
        print("  Nenhum quarto disponível no momento.")
        pause()
        return

    print("\n  Quartos disponíveis:")
    for q in disponiveis:
        print(fmt_room(q))

    numero = input_int("Número do quarto desejado: ")
    quarto = controller.get_all_rooms().get(numero)

    if not quarto:
        print("  Quarto não encontrado.")
        pause()
        return
    if quarto.get('occupied'):
        print("  Quarto indisponível no momento.")
        pause()
        return

    checkin = input_date("Data de Check-in")
    checkout = input_date("Data de Check-out")

    if checkout < checkin:
        print("  Erro: Check-out deve ser posterior ao Check-in.")
        pause()
        return

    global _booking_counter
    booking = Booking(cliente, quarto, checkin, checkout)
    controller.reqBooking(booking)
    _booking_counter += 1
    pause()


def cancelar_reserva_cliente(cliente: dict):
    cancelaveis = [
        b for b in controller.get_all_bookings().values()
        if b.get('client_cpf') == cliente.get('cpf') and not b.get('active')
    ]

    if not cancelaveis:
        print("  Nenhuma reserva cancelável.\n"
              "  (Reservas com check-in ativo precisam de check-out primeiro.)")
        pause()
        return

    for b in cancelaveis:
        print(fmt_booking(b))

    b_id = input_int("ID da reserva a cancelar: ")

    booking = controller.get_all_bookings().get(b_id)
    
    # Comparação direto pelo dict, ou seja, sem .get_client().get_cpf()
    if not booking or booking.get('client_cpf') != cliente.get('cpf'):
        print("  Reserva não encontrada ou não pertence a você.")
        pause()
        return

    controller.remove_booking(b_id)
    pause()
    




#-------------------------------------------------------------------------------------------------
#menu admin
def menu_admin_login():
    print("\nLogin Administrativo")
    senha = input("  Senha: ").strip()

    if not controller.accessAuthentication(senha):
        pause()
        return  # Retorna ao menu principal (acesso negado ou bloqueado)

    menu_admin()


def menu_admin():
    while True:
        print("\nPAINEL ADMINISTRATIVO")
        print("  1 · Gerenciar Quartos")
        print("  2 · Gerenciar Reservas")
        print("  3 · Gerenciar Clientes")
        print("  4 · Realizar Check-in")
        print("  5 · Realizar Check-out")
        print("  0 · Sair do painel")
        opt = input("  Escolha: ").strip()

        match opt:
            case "1": menu_admin_quartos()
            case "2": menu_admin_reservas()
            case "3": menu_admin_clientes()
            case "4": admin_checkin()
            case "5": admin_checkout()
            case "0": break
            case _: print("  Opção inválida.")


#admin: quartos
def menu_admin_quartos():
    while True:
        print("\nQUARTOS")
        print("  1 · Listar todos")
        print("  2 · Cadastrar quarto")
        print("  3 · Remover quarto")
        print("  0 · Voltar")
        opt = input("  Escolha: ").strip()

        match opt:
            case "1": admin_listar_quartos()
            case "2": admin_cadastrar_quarto()
            case "3": admin_remover_quarto()
            case "0": break
            case _: print("  Opção inválida.")


def admin_listar_quartos():
    print("\n  ── Todos os Quartos ──")
    quartos = controller.get_all_rooms()
    if not quartos:
        print("  Nenhum quarto cadastrado.")
    else:
        for q in quartos.values():
            print(fmt_room(q))
    pause()


def admin_cadastrar_quarto():
    print("\nCadastrar Quarto")
    numero = input_int("Número: ")
    max_pessoas = input_int("Capacidade máxima de pessoas: ")
    preco = input_float("Preço da diária (R$): ")
    quarto = Room(numero, max_pessoas, preco, False)
    controller.register_room(quarto)
    pause()


def admin_remover_quarto():
    print("\nRemover Quarto ")
    admin_listar_quartos()
    numero = input_int("Número do quarto a remover: ")
    controller.remove_room(numero)
    pause()


#admin: reservas
def menu_admin_reservas():
    while True:
        print("\nRESERVAS")
        print("  1 · Listar todas")
        print("  2 · Cancelar reserva")
        print("  0 · Voltar")
        opt = input("  Escolha: ").strip()

        match opt:
            case "1": admin_listar_reservas()
            case "2": admin_cancelar_reserva()
            case "0": break
            case _: print("  Opção inválida.")


def admin_listar_reservas():
    print("\n  Todas as Reservas")
    reservas = controller.get_all_bookings()
    if not reservas:
        print("  Nenhuma reserva registrada.")
    else:
        for b in reservas.values():
            print(fmt_booking(b))
    pause()


def admin_cancelar_reserva():
    print("\n  Cancelar Reserva")
    admin_listar_reservas()
    b_id = input_int("ID da reserva a cancelar: ")
    controller.remove_booking(b_id)
    pause()

#admin com clientes(Ver, check-in/-out, )
def menu_admin_clientes():
    while True:
        print("\nCLIENTES")
        print("  1 · Listar todos")
        print("  2 · Cadastrar cliente")
        print("  3 · Ver reservas de um cliente")
        print("  0 · Voltar")
        opt = input("  Escolha: ").strip()

        match opt:
            case "1": admin_listar_clientes()
            case "2": cadastrar_cliente()
            case "3": admin_reservas_por_cliente()
            case "0": break
            case _: print("  Opção inválida.")


def admin_listar_clientes():
    print("\n  Todos os Clientes")
    clientes = controller.get_all_clients()
    if not clientes:
        print("  Nenhum cliente cadastrado.")
    else:
        for c in clientes.values():
            print(f"  CPF: {c.get('cpf')} | Nome: {c.get('name')} | Idade: {c.get('age')}")
    pause()


def admin_reservas_por_cliente():
      print("\n  Reservas por Cliente")
      admin_listar_clientes()
      cpf = input("  CPF do cliente: ").strip()
      cliente = controller.get_all_clients().get(cpf)

      if not cliente:
        print("  Cliente não encontrado.")
        pause()
        return

      reservas = [
        b for b in controller.get_all_bookings().values()
        if b.get('client_cpf') == cpf
    ]

      if not reservas:
        print(f"  {cliente.get('name')} não possui reservas.")
      else:
        for b in reservas:
            print(fmt_booking(b))
      pause()

def admin_checkin():
    print("\n  Realizar Check-in")
    #mostra as reservas sem check-in ativo
    pendentes = [b for b in controller.get_all_bookings().values() if not b.get('active')]
    if not pendentes:
        print("  Nenhuma reserva aguardando check-in.")
        pause()
        return
    for b in pendentes:
        print(fmt_booking(b))

    b_id = input_int("ID da reserva: ")
    controller.checkIn(b_id)
    pause()


def admin_checkout():
    print("\n  Realizar Check-out")
    #mostra as reservas com check-in ativo
    ativas = [b for b in controller.get_all_bookings().values() if b.get('active')]
    if not ativas:
        print("  Nenhum hóspede com check-in ativo no momento.")
        pause()
        return
    for b in ativas:
        print(fmt_booking(b))

    b_id = input_int("ID da reserva: ")
    controller.checkOut(b_id)
    pause()

if __name__ == "__main__":
    start()