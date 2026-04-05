from datetime import date
from models.client import Client
from models.room import Room

class Booking:
    _id_counter=1

    def __init__(self, client: Client, room: Room, checkin: date, checkout :date):
        self._id_counter= Booking._id_counter
        Booking._id_counter+=1

        self._client= client
        self._room= room
        self._checkin= checkin
        self._active= False
        self._checkin = checkin
        self._checkout = checkout
        dailys = (checkout - checkin).days
        if dailys <= 0:
          self._total_expense = 1* self._room.get_daily_price()
        else:
          self._total_expense = dailys*self._room.get_daily_price()
    
    #getters
    def get_id(self):
        return self._id_counter

    def get_client(self):
        return self._client

    def get_room(self):
        return self._room

    def get_checkin(self):
        return self._checkin
    
    def get_checkout(self):
        return self._checkout

    def get_total_expense(self) -> float:
        return self._total_expense
    
    def get_active(self):
        return self._active
    
    #setters
    def set_client(self, client):
        self._client = client

    def set_active(self, active: bool):
        self._active = active

    def set_room(self, room):
        self._room = room

    def set_checkin(self, checkin):
        self._checkin = checkin

    def set_checkout(self, checkout):
        self._checkout = checkout



