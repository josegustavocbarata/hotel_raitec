class Room:
    _id_counter=1
    def __init__(self, number: int, max_people: int, daily_price: float, occupied):
        self._id=Room._id_counter
        Room._id_counter+=1

        self.__number = number
        self.__max_people = max_people
        self._daily_price = daily_price
        self.__occuppied = occupied
    
    #getters
    def get_id_quarto(self):
        return self.__id_quarto
    
    def get_number(self):
        return self.__number
    
    def get_max_people(self):
        return self.__max_people
    
    def get_daily_price(self):
        return self._daily_price

    def get_occupied(self):
        return self.__occuppied
    
    #setters
    def set_id_quarto(self, id_quarto): 
        self.__id_quarto = id_quarto
    
    def set_number(self, number):
        self.__number = number
    
    def set_max_people(self, max_people):
        self.__max_people = max_people
    
    def set_daily_price(self, daily_price):
        self._daily_price = daily_price
    
    def set_occupied(self, status):
        self.__occuppied = status