from models.client import Client
from models.room import Room
from models.booking import Booking
from controllers.hotel_controller import HotelController
from datetime import date, timedelta

def testar_sistema():
    controller = HotelController()

    print("\n--- 1. TESTE DE AUTENTICAÇÃO ---")
    if not controller.accessAuthentication("teste"):
        return

    print("\n--- 2. TESTE DE REGISTRO DE QUARTOS ---")
    # Criando 3 tipos de quartos para teste
    quartos_teste = [
        Room(101, "Simples", 150.0, False),
        Room(102, "Duplo", 250.0, False),
        Room(201, "Luxo", 500.0, False)
    ]
    for q in quartos_teste:
        controller.register_room(q)

    print("\n--- 3. TESTE DE REGISTRO DE CLIENTES (POPOULANDO 20) ---")
    for i in range(1, 21):
        # Gerando CPFs e Nomes fictícios para preencher o requisito
        cpf = f"{i:03d}.000.000-{i:02d}"
        nome = f"Cliente Exemplo {i}"
        idade = 20 + i
        cliente = Client(nome, idade, cpf)
        controller.register_client(cliente)

    print("\n--- 4. TESTE DE RESERVA (REQBOOKING) ---")
    # Criando uma reserva para o cliente 1 no quarto 101
    cliente_vlp = Client("Cliente Exemplo 1", 21, "001.000.000-01")
    quarto_vlp = Room(101, 2, 150.00, False)
    
    hoje = date.today()
    amanha = hoje + timedelta(days=2)
    
    reserva = Booking(cliente_vlp, quarto_vlp, hoje, amanha)
    controller.reqBooking(reserva)

    print("\n--- 5. TESTE DE INSIGHTS (LISTAGEM) ---")
    print("Listando Clientes Cadastrados:")
    print(controller.get_all_clients())

    print("\n--- 6. TESTE DE FLUXO (CHECK-IN E CHECK-OUT) ---")
    # Buscamos o ID da reserva que acabou de ser criada
    reservas = controller.get_all_bookings()
    if reservas:
        reserva_id = reservas[0]['id']
        
        # Realiza Check-in
        controller.checkIn(reserva_id)
        
        # Realiza Check-out (isso deve liberar o quarto e deletar a reserva)
        controller.checkOut(reserva_id)

if __name__ == "__main__":
    testar_sistema()