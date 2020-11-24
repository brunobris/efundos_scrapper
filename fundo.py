import json

class Fundo:
    def __init__(self, symbol, admin, razao_social, detalhe=None):
        self.symbol  = symbol
        self.admin = admin
        self.razao_social = razao_social
        self.detalhe = detalhe

    def toJson(self):
         return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False)