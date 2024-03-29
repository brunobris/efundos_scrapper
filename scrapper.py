import requests, time, json, base64
from fundo import Fundo
from detalhe import Detalhe
from bs4 import BeautifulSoup
from models.dados_b3 import DadosB3
import re, random
#from b3_service import buscar_documentos_do_fundo
from fnet_service import buscar_documentos_do_fundo
from b3_service import buscar_dividendos_do_fundo, buscar_dados_do_fundo, buscar_desdobramentos_do_fundo
#AWS LAMBDA
def lambda_handler(event, context):
    obtem_fundos()


conteudo = """ 
"""

URL_BASE = "https://www.fundsexplorer.com.br/funds"
#soup = BeautifulSoup(conteudo, 'html.parser')


#def obtem_lista_fundos():

#TODO: Migrar lista para B3?
def obtem_fundos():
    pagina_lista_fundos = requests.get(URL_BASE)

    soup = BeautifulSoup(pagina_lista_fundos.content, 'html.parser')
    lista_fiis = soup.find_all("div", class_="item")
    print(str(len(lista_fiis)) + ' fundo(s) encontrado(s)')

    #Randomiza lista
    random.shuffle(lista_fiis)
    for (indice, fii) in enumerate(lista_fiis):
        symbol_el = fii.find("span", class_="symbol")
        symbol = symbol_el.text.strip()

        #Quando quiser testar apenas um fundo especifico
        if symbol != "CXRI11":
            continue
        
        print('Fundo ' + str(indice + 1) + ' de ' + str(len(lista_fiis)))
        try:
            if symbol_el:
                razao_social = fii.find("span", class_="name").text.strip()
                admin = fii.find("span", class_="admin").text.strip() if  fii.find("span", class_="admin") else None

                print('Obtendo dados do fundo : ' + symbol)

                fundo = Fundo(symbol, admin, razao_social)

                #Busca detalhes do fundo
                detalhe_fundo(fundo)


                print(fundo.toJson())
                
                #enviar_webservice(fundo.toJson())
                
                #break
        except Exception as e:
            print('### Erro no fundo {}'.format(symbol))
            print('### Detalhes: {}'.format(e))
            #break
            continue
        finally:
            time.sleep(0.2)

def detalhe_fundo(fundo):
    print('Carregando página de detalhe...')
    pagina_detalhe = requests.get(URL_BASE + "/" + fundo.symbol)
    detalheSoup = BeautifulSoup(pagina_detalhe.content, 'html.parser')

    print('Carregado.')
    # Ler informações do fundo
    info_basica = detalheSoup.find_all("section", {"id": "basic-infos"})[0]
    cnpj_fundo = info_basica.find_all("span", class_="description")[8].get_text(strip=True)
    cnpj_fundo = ''.join(re.findall(r'\d+', cnpj_fundo))

    #Grava CNPJ do Fundo:
    fundo.cnpj = cnpj_fundo

    # Ler dados
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
    lista_doc = ler_documentos(cnpj_fundo)

    #Eventos do fundo
    dadosB3 = DadosB3(ler_eventos(cnpj_fundo, fundo.symbol[:4]))
    dadosB3.lista_dividendos = ler_dividendos(dadosB3.dados)
    dadosB3.lista_desdobramentos = ler_desdobramentos(dadosB3.dados)
    

    #print(lista_dividendos)
    detalhe = Detalhe(liquidez_diaria,
                      ultimo_rendimento, 
                      dy, 
                      patrimonio_liquido,
                      valor_patrimonal,
                      rentabilidade_mes,
                      lista_doc,
                      dadosB3.lista_dividendos,
                      dadosB3.lista_desdobramentos)
    
    fundo.detalhe = detalhe

def ler_documentos(cnpj):
    return buscar_documentos_do_fundo(cnpj)

def ler_eventos(cnpj, symbol):
    return buscar_dados_do_fundo(cnpj, symbol)

def ler_dividendos(dados):
    return buscar_dividendos_do_fundo(dados)

def ler_desdobramentos(dados):
    return buscar_desdobramentos_do_fundo(dados)


def enviar_webservice(dados):
    url = "http://localhost:9092/fundos/atualizar-fundo"
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': 'application/json',
        'Accept-Charset': 'utf-8'
    }
    #print(dados)
    r = requests.post(url, json=json.loads(dados), headers=headers)

    if r.status_code != 200:
        raise Exception('Erro ao enviar dados do fundo para o server. StatusCode {}'.format(r.status_code))

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

#fundo = Fundo("YCHY11", "", "")

#print(fundo.symbol)
#detalhe_fundo(fundo)