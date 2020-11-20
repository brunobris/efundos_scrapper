import datetime, json, base64
import requests
import urllib3

urllib3.disable_warnings()

B3_BASE_URL = "https://sistemaswebb3-listados.b3.com.br"
DOCUMENTS_URL = "/fundsProxy/fundsCall/GetListedDocuments"

now = datetime.datetime.now()

#data_atual_request = now.strftime("%Y-%m-%d")
#print(data_atual)



def get_request(url):
    return requests.get(url, verify=False)

def buscar_documentos_do_fundo(cnpj):
    #Parametro que será convertido em Base64 para o request
    #TODO: Utilizar datas (mês anterior e data atual)
    documentos_fundo_param = {"pageNumber":1,"pageSize":10,"cnpj":cnpj,"dateInitial":"2020-09-18","dateFinal":"2020-11-17","category": None}
    parametro_base64 = base64.b64encode(json.dumps(documentos_fundo_param, separators=(',', ':')).encode('utf8'))
    url_request = B3_BASE_URL + DOCUMENTS_URL + "/" + str(parametro_base64.decode('utf8'))

    result = get_request(url_request)

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



#buscar_documentos_do_fundo('18979895000113')
