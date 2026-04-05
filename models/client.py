class Client: 
    _id_counter=1

    def __init__(self, name: str, age: int, cpf: str):
        self._id= Client._id_counter
        Client._id_counter+=1

        self._name= name
        self._age= age
        self._cpf= cpf
    
    # getters
    def get_id(self) ->int:
        return self._id
    
    def get_name(self) -> str:
        return self._name

    def get_age(self) -> int:
        return self._age
    
    def get_cpf(self) -> str:
        return self._cpf
    
