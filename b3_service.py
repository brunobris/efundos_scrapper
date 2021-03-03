import json, base64
import requests
from datetime import date, datetime
from dateutil import parser
from http_requests import http_get
from util.date_functions import converter_data
import urllib3

urllib3.disable_warnings()

B3_BASE_URL = "https://sistemaswebb3-listados.b3.com.br"
DOCUMENTS_URL = "/fundsProxy/fundsCall/GetListedDocuments"
DIVIDEND_URL = "/fundsProxy/fundsCall/GetListedSupplementFunds"

#data_atual_request = now.strftime("%Y-%m-%d")
#print(data_atual)

def deprecated_buscar_documentos_do_fundo(cnpj):
    #Parametro que será convertido em Base64 para o request
    #TODO: Utilizar datas (mês anterior e data atual)
    documentos_fundo_param = {"pageNumber":1,"pageSize":10,"cnpj":cnpj,"dateInitial":"2020-09-18","dateFinal":"2020-11-17","category": None}
    parametro_base64 = base64.b64encode(json.dumps(documentos_fundo_param, separators=(',', ':')).encode('utf8'))
    url_request = B3_BASE_URL + DOCUMENTS_URL + "/" + str(parametro_base64.decode('utf8'))

    result = http_get(url_request)

    if result.status_code != 200:
        return []

    resultado = json.loads(result.text)
    #Ordena de modo descrescente por data de publicacao dos documentos
    resultado['results'].sort(key=lambda x: x['deliveryDate'], reverse=True)

    lista = [
                {
                    'nome' : doc['category']['describle'] + ' - ' + doc['referenceDateFormat'],
                    'link' : doc['urlFundosNet'],
                    'data_referencia' : doc['referenceDate'],
                    'data_publicacao' : doc['deliveryDate']
                } for doc in resultado['results']
            ]

    return lista

def buscar_dados_do_fundo(cnpj, symbol):
    #Parametro que será convertido em Base64 para o request
    #TODO: Utilizar datas (mês anterior e data atual)
    parametro = {"cnpj":cnpj,"identifierFund":symbol,"typeFund":7}
    parametro_base64 = base64.b64encode(json.dumps(parametro, separators=(',', ':')).encode('utf8'))

    url_request = B3_BASE_URL + DIVIDEND_URL + "/" + str(parametro_base64.decode('utf8'))
    
    print('Obtendo eventos da URL: ' + url_request)
    result = http_get(url_request)
    if result.status_code != 200:
            raise Exception('status_code inesperado ao obter eventos do fundo: {}'.format(result.status_code))

    if not result.text:
        return []
    
    return json.loads(result.text)

def buscar_dividendos_do_fundo(dados): 
    #Filtra apenas CTF (COTA FUNDO) no isinCode, ex BRCPTSCTF004
    #TODO: Inverter ordem? Talvez apenas para carga inicial
    #resultado['cashDividends'].sort(key=lambda x: converter_data(x['paymentDate']))
    return [
                {
                    'data_base' : converter_data(doc['lastDatePrior']),
                    'data_pagamento' : converter_data(doc['paymentDate']),
                    'rendimento' : f'{float(doc["rate"].replace(".", "").replace(",", ".")):.2f}',
                } for doc in dados['cashDividends'] if 'CTF' in doc['isinCode'][6:] and doc['label'] == 'RENDIMENTO'
            ]

def buscar_desdobramentos_do_fundo(dados): 
    #Filtra apenas CTF (COTA FUNDO) no isinCode, ex BRCPTSCTF004
    #TODO: Inverter ordem? Talvez apenas para carga inicial
    #resultado['cashDividends'].sort(key=lambda x: converter_data(x['paymentDate']))
    return [
                {
                    'data_deliberacao' : converter_data(doc['approvedOn']),
                    'data_negocios_ate' : converter_data(doc['lastDatePrior']),
                    'fator' : f'{float(doc["factor"].replace(".", "").replace(",", ".")):.2f}',
                } for doc in dados['stockDividends'] if doc['label'] == 'DESDOBRAMENTO'
            ]



#print(buscar_dividendos_do_fundo('18979895000113', 'CPTS'))
#print(buscar_dividendos_do_fundo('17098794000170', 'CXRI'))
#print(buscar_dividendos_do_fundo('28267696000136', 'YCHY'))




