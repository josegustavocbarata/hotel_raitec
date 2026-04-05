import mysql.connector
from mysql.connector import Error
from models.client import Client
from models.room import Room
from models.booking import Booking
from repository.connection import DatabaseManager
import os

class HotelController:
    def __init__(self):
        self.__login_attempts = 0
        self.__admin_password = os.getenv("ADMIN_PASSWORD", "teste")
        
    # --- AUTENTICAÇÃO ---
    def accessAuthentication(self, password: str) -> bool:
        MAX_ATTEMPTS = 3 
        if self.__login_attempts >= MAX_ATTEMPTS:
            print("ACESSO BLOQUEADO: Limite de tentativas excedido.")
            return False

        if password == self.__admin_password:
            self.__login_attempts = 0 
            print("Autenticação bem-sucedida!")
            return True
        else:
            self.__login_attempts += 1
            print(f"Erro: Senha incorreta! Tentativas restantes: {MAX_ATTEMPTS - self.__login_attempts}")
            return False

    # --- CLIENTES --- REGISTRO --- 
    def register_client(self, client: Client):
        if not isinstance(client, Client):
            print("Erro: Objeto inválido, objeto deve ser do tipo Client")
            return

        query = "INSERT INTO clients (cpf, name, age) VALUES (%s, %s, %s)"
        values = (client.get_cpf(), client.get_name(), client.get_age())

        # Abre a conexão 
        conn = DatabaseManager.get_connection()
        
        if conn:
            try:
                # O 'with' garante que o cursor.close() seja chamado ao sair do bloco
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    conn.commit()
                    print(f"Cliente {client.get_name()} registrado com sucesso!")
            
            except mysql.connector.IntegrityError as err:
                if err.errno == 1062:
                    print(f"Erro: O CPF {client.get_cpf()} já existe.")
                else:
                    print(f"Erro de integridade: {err}")
            
            except Exception as e:
                print(f"Erro inesperado: {e}")
                
            finally:
                # Fecha a conexão aqui 
                if conn.is_connected():
                    conn.close()

    # --- QUARTOS --- REGISTRO --- 

    def register_room(self, room: Room):
        if not isinstance(room, Room):
            print("Erro: Objeto fornecido não é um Quarto válido.")
            return

        query = "INSERT INTO rooms (number, max_people, daily_price, occupied) VALUES (%s, %s, %s, %s)"
        values = (room.get_number(), room.get_max_people(), room.get_daily_price(), room.get_occupied())

        conn = DatabaseManager.get_connection()
        if conn:
            try:
                # O 'with' cuida do cursor.close() automaticamente ao sair do bloco
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                    conn.commit()
                    print(f"✅ Quarto {room.get_number()} cadastrado com sucesso!")
            
            except mysql.connector.IntegrityError:
                print(f"Erro: O quarto número {room.get_number()} já está cadastrado.")
                
            except Exception as e:
                print(f"Erro inesperado ao registrar quarto: {e}")
                
            finally:
                # Mantemos o fechamento da conexão no finally para garantir a liberação do slot no Aiven
                if conn.is_connected():
                    conn.close()
    #   QUARTOS --- REMOVER QUARTO ---
    def remove_room(self, room_number: int):
        conn = DatabaseManager.get_connection()
        if not conn:
            return

        query = "DELETE FROM rooms WHERE number = %s"

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (room_number,))
                conn.commit()

                if cursor.rowcount > 0:
                    print(f"Quarto {room_number} removido com sucesso!")
                else:
                    print(f"Quarto {room_number} não encontrado.")

        except mysql.connector.IntegrityError:
            print(f"Erro: Não é possível remover o quarto {room_number} pois ele possui reservas vinculadas.")
        except mysql.connector.Error as err:
            print(f"Erro ao remover quarto: {err}")
            conn.rollback()
        finally:
            if conn.is_connected():
                conn.close()

    # RESERVAS --- REMOVER RESERVA ---
    def remove_booking(self, booking_id: int):
        conn = DatabaseManager.get_connection()
        if not conn:
            return

        query = "DELETE FROM bookings WHERE id = %s"

        try:
            with conn.cursor() as cursor:
                cursor.execute(query, (booking_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    print(f"Reserva {booking_id} removida com sucesso!")
                else:
                    print(f"Nenhuma reserva encontrada com o ID {booking_id}.")
        
        except mysql.connector.Error as err:
            print(f"Erro ao remover reserva: {err}")
            conn.rollback()
        finally:
            if conn.is_connected():
                conn.close()

    # --- RESERVAS (Fluxo Completo) ---
    def reqBooking(self, booking: Booking):
        # 1. Extração de dados do objeto
        room = booking.get_room()
        room_num = room['number']
        checkin = booking.get_checkin()
        checkout = booking.get_checkout()
        client_cpf = booking.get_client()['cpf']

        # Verifica se há qualquer sobreposição de datas para o mesmo quarto
        check_query = """
            SELECT id FROM bookings 
            WHERE room_number = %s 
            AND NOT (%s >= checkout OR %s <= checkin)
        """
        
        insert_query = """
            INSERT INTO bookings (client_cpf, room_number, checkin, checkout)
            VALUES (%s, %s, %s, %s)
        """

        # Gerenciamento de Conexão com a Nuvem 
        conn = DatabaseManager.get_connection() 
        
        if conn:
            try:
                # Usando 'with' para garantir que o cursor feche automaticamente
                with conn.cursor() as cursor:
                    # Verificar disponibilidade
                    cursor.execute(check_query, (room_num, checkin, checkout))
                    
                    if cursor.fetchone():
                        print(f" Erro: O quarto {room_num} já está ocupado entre {checkin} e {checkout}!")
                    else:
                        # Realizar a reserva
                        cursor.execute(insert_query, (
                            client_cpf, 
                            room_num, 
                            checkin, 
                            checkout
                        ))
                        conn.commit()
                        print(f"  Reserva no quarto {room_num} solicitada com sucesso!")
            
            except mysql.connector.Error as err:
                print(f"Erro no banco de dados: {err}")
            
            except Exception as e:
                print(f"Erro inesperado: {e}")
                
            finally:
                # Fecha a conexão 
                if conn.is_connected():
                    conn.close()

# --- CHECK-IN / CHECK-OUT ---
    
    def checkIn(self, booking_id: int):
        conn = DatabaseManager.get_connection()
        if not conn:
            return

        try:
            # O 'with' garante que o cursor seja fechado automaticamente
            with conn.cursor() as cursor:
                # 1. Ativa a reserva (muda status para ativo)
                cursor.execute("UPDATE bookings SET active = 1 WHERE id = %s", (booking_id,))
                
                # 2. Ocupa o quarto associado a essa reserva específica
                cursor.execute("""
                    UPDATE rooms SET occupied = 1 
                    WHERE number = (SELECT room_number FROM bookings WHERE id = %s)
                """, (booking_id,))
                
                # Só salvamos se ambos os comandos acima correrem bem
                conn.commit()
                print(f"🔔 Check-in realizado com sucesso! (ID Reserva: {booking_id})")
        
        except mysql.connector.Error as err:
            print(f"❌ Erro de banco de dados no Check-in: {err}")
            conn.rollback() # Reverte alterações se algo falhar no meio
        finally:
            if conn.is_connected():
                conn.close()

    def checkOut(self, booking_id: int):
        conn = DatabaseManager.get_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cursor:
                # 1. Libera o quarto antes de apagar a reserva (subquery)
                cursor.execute("""
                    UPDATE rooms SET occupied = 0 
                    WHERE number = (SELECT room_number FROM bookings WHERE id = %s)
                """, (booking_id,))
                
                # 2. Remove a reserva do sistema 
                cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
                
                conn.commit()
                print(f"Check-out finalizado para a reserva {booking_id}. Quarto liberado!")
        
        except mysql.connector.Error as err:
            print(f"❌ Erro de banco de dados no Check-out: {err}")
            conn.rollback()
        finally:
            if conn.is_connected():
                conn.close()

# --- INSIGHTS E LISTAGENS ---

    def get_all_clients(self):
        """Retorna um dicionário onde a chave é o CPF e o valor são os dados do cliente."""
        conn = DatabaseManager.get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM clients")
                lista_clientes = cursor.fetchall()
                # Transforma a lista em dicionário: { '123': {'name': 'Levi', ...}, '456': {...} }
                return {cliente['cpf']: cliente for cliente in lista_clientes}
        except mysql.connector.Error as err:
            print(f"❌ Erro ao buscar clientes: {err}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()

    def get_all_rooms(self):
        """Retorna um dicionário com o número do quarto como chave."""
        conn = DatabaseManager.get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM rooms")
                lista_quartos = cursor.fetchall()
                
                return {quarto['number']: quarto for quarto in lista_quartos}
        except mysql.connector.Error as err:
            print(f"❌ Erro ao buscar quartos: {err}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()

    def get_all_bookings(self):
        """Retorna um dicionário com o ID da reserva como chave."""
        conn = DatabaseManager.get_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(dictionary=True) as cursor:
                query = """
                    SELECT b.id, c.name as client_name, b.room_number, 
                        b.checkin, b.checkout, b.active 
                    FROM bookings b
                    JOIN clients c ON b.client_cpf = c.cpf
                """
                cursor.execute(query)
                lista_reservas = cursor.fetchall()
                return {reserva['id']: reserva for reserva in lista_reservas}
        except mysql.connector.Error as err:
            print(f"❌ Erro ao buscar reservas: {err}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()

    def get_available_rooms(self):
        """Retorna apenas os quartos que não estão ocupados."""
        conn = DatabaseManager.get_connection()
        if not conn: return []
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM rooms WHERE occupied = 0")
                return cursor.fetchall()
        finally:
            if conn.is_connected(): conn.close()

    def find_client_by_cpf(self, cpf: str):
        """Busca um cliente específico pelo CPF."""
        conn = DatabaseManager.get_connection()
        if not conn: return None
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM clients WHERE cpf = %s", (cpf,))
                return cursor.fetchone()
        finally:
            if conn.is_connected(): conn.close()