import json

class Detalhe:
    def __init__(self, 
        liquidez_diaria, 
        ultimo_rendimento, 
        dy, 
        patrimonio_liquido, 
        valor_patrimonial,
        rentabilidade_mes,
        lista_documentos,
        lista_dividendos,
        lista_desdobramentos):
        self.liquidez_diaria = liquidez_diaria
        self.ultimo_rendimento = ultimo_rendimento
        self.dy = dy
        self.patrimonio_liquido = patrimonio_liquido
        self.valor_patrimonial = valor_patrimonial
        self.rentabilidade_mes = rentabilidade_mes
        self.lista_documentos = lista_documentos
        self.lista_dividendos = lista_dividendos
        self.lista_desdobramentos = lista_desdobramentos


    def toJson(self):
         return json.dumps(self, default=lambda o: o.__dict__, ensure_ascii=False)