import json

class Fundo:
    def __init__(self, symbol, admin, nome, detalhe=None):
        self.symbol  = symbol
        self.admin = admin
        self.nome = nome
        self.detalhe = detalhe

    def toJson(self):
         return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False)