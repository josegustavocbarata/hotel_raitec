class Admin:
    _id_counter=1

    def __init__(self, login: str, password: int):
        self._id= Admin._id_counter
        Admin._id_counter+=1

        self._login= login
        self._password= password
    
    #getters
    def get_id(self):
        return self._id

    def get_login(self):
        return self._login

    def get_password(self):
        return self._password

    #setters
    def set_login(self, login):
        self._login = login

    def set_password(self, password):
        if len(str(password)) >= 4:
            self._password = password
        else:
            print("Erro: A senha deve ter pelo menos 4 dígitos.")
            #arrumar loop para manter até senha adequada