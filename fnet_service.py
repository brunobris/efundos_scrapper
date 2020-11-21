import requests, json
from datetime import date, datetime
from dateutil import parser
from http_requests import http_get
import urllib3

URL_DOC_FNET = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=4&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo="
URL_LINK_DOC = "https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id="

urllib3.disable_warnings()

def converter_data(data_string):
    return str(parser.parse(data_string, dayfirst=True, default=datetime(2020, 1, 1)))

def buscar_documentos_do_fundo(cnpj):
    url_request = URL_DOC_FNET + cnpj

    print('Obtendo documentos da URL: ' + url_request)
    result = http_get(url_request)
    if result.status_code != 200:
        raise Exception('status_code inesperado ao obter documentos: {}'.format(result.status_code))

    resultado = json.loads(result.text)
    return [
                {
                    'nome' : doc['categoriaDocumento'] + ' - ' + doc['dataReferencia'],
                    'fnet_id' : str(doc['id']),
                    'data_referencia' : converter_data(doc['dataReferencia']),
                    'data_publicacao' : converter_data(doc['dataEntrega'])
                } for doc in resultado['data']
            ]

#buscar_documentos_do_fundo('35765826000126')
