import requests, time, json
from fundo import Fundo
from detalhe import Detalhe
from bs4 import BeautifulSoup

#AWS LAMBDA
def lambda_handler(event, context):
    obtem_fundos()


conteudo = """ 
"""

URL_BASE = "https://www.fundsexplorer.com.br/funds"
#soup = BeautifulSoup(conteudo, 'html.parser')


def obtem_fundos():
    pagina_lista_fundos = requests.get(URL_BASE)

    soup = BeautifulSoup(pagina_lista_fundos.content, 'html.parser')
    lista_fiis = soup.find_all("div", class_="item")
    print(str(len(lista_fiis)) + ' fundo(s) encontrado(s)')


    for (indice, fii) in enumerate(lista_fiis):
        print('Fundo ' + str(indice + 1) + ' de ' + str(len(lista_fiis)))
        symbol_el = fii.find("span", class_="symbol")
        if symbol_el:
            symbol = symbol_el.text.strip()
            name = fii.find("span", class_="name").text.strip()
            admin = fii.find("span", class_="admin").text.strip() if  fii.find("span", class_="admin") else None

            print('Obtendo dados do fundo : ' + symbol)

            fundo = Fundo(symbol, admin, name)

            #Busca detalhes do fundo
            detalhe_fundo(fundo)

            enviar_webservice(fundo.toJson())

def detalhe_fundo(fundo):
    pagina_detalhe = requests.get(URL_BASE + "/" + fundo.symbol)
    detalheSoup = BeautifulSoup(pagina_detalhe.content, 'html.parser')
    liquidez_diaria = detalheSoup.find_all("span", class_="indicator-value")[0].get_text(strip=True)
    ultimo_rendimento = detalheSoup.find_all("span", class_="indicator-value")[1].get_text(strip=True)
    
    dy = detalheSoup.find_all("span", class_="indicator-value")[2].get_text(strip=True)
    patrimonio_liquido = detalheSoup.find_all("span", class_="indicator-value")[3].get_text(strip=True)
    valor_patrimonal = detalheSoup.find_all("span", class_="indicator-value")[4].get_text(strip=True)
    rentabilidade_mes = detalheSoup.find_all("span", class_="indicator-value")[5].get_text(strip=True)
    #pvp = detalheSoup.find_all("span", class_="indicator-value")[6].get_text(strip=True)


    #Realiza tratamento
    liquidez_diaria = liquidez_diaria.replace('.', '') if liquidez_diaria != "N/A" else None
    ultimo_rendimento = ultimo_rendimento.replace('R$ ', '').replace(',', '.') if ultimo_rendimento != "N/A" else None
    dy = dy.replace('%', '').replace(',', '.') if dy != "N/A" else None
    patrimonio_liquido = tratar_patrimonio_liquido(patrimonio_liquido.replace('R$ ', '').replace(',', '.')) if patrimonio_liquido != "N/A" else None
    
    valor_patrimonal = valor_patrimonal.replace('R$ ', '').replace('.', '',).replace(',', '.') if valor_patrimonal != "N/A" else None
    rentabilidade_mes = rentabilidade_mes.replace('%', '').replace(',', '.') if rentabilidade_mes != "N/A" else None

    #Realiza leitura dos documentos do fundo
    lista_doc = ler_documentos(detalheSoup)

    detalhe = Detalhe(liquidez_diaria,
                      ultimo_rendimento, 
                      dy, 
                      patrimonio_liquido,
                      valor_patrimonal,
                      rentabilidade_mes,
                      lista_doc)
    
    fundo.detalhe = detalhe
    time.sleep(0.2)

def ler_documentos(detalheSoup):
    lista = detalheSoup.find_all("a", class_="bulletin-text-link")
    return [{"titulo" : doc.get_text(strip=True), "link" : doc['href']} for doc in lista]


def enviar_webservice(dados):
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8'
    }
    print(dados)
    r = requests.post("http://localhost:9092/fundos/atualizar-fundo",
                      json=json.loads(dados),
                      headers=headers)

    if r.status_code != 200:
        print(r.status_code)
        print(r.text)

def tratar_patrimonio_liquido(pl):
    patrimonio_liquido = 0
    if pl.endswith('mi') :
        #MILHOES
        patrimonio_liquido = float(pl.replace('mi', '').strip())
        patrimonio_liquido = patrimonio_liquido * 1000000
    elif pl.endswith('bi'):
        #BILHOES
        patrimonio_liquido = float(pl.replace('bi', '').strip())
        patrimonio_liquido = patrimonio_liquido * 1000000000
    else:
        #MIL
        patrimonio_liquido = float(pl.replace('.', ''))

    return patrimonio_liquido

obtem_fundos()