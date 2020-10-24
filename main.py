import requests, time
from bs4 import BeautifulSoup

# def lambda_handler(event, context):
#     r = requests.get("https://ifconfig.me")
#     print(r.text)


conteudo = """ 
"""

URL_BASE = "https://www.fundsexplorer.com.br/funds"
#soup = BeautifulSoup(conteudo, 'html.parser')


def obtem_fundos():
    pagina_lista_fundos = requests.get(URL_BASE)

    soup = BeautifulSoup(pagina_lista_fundos.content, 'html.parser')
    lista_fiis = soup.find_all("div", class_="item")
    for fii in lista_fiis:
        admin_el = fii.find("span", class_="admin")
        if admin_el:
            admin = admin_el.text.strip()
            symbol = fii.find("span", class_="symbol").text.strip()
            name = fii.find("span", class_="name").text.strip()
            
            print(symbol + " | " + admin + " | " + name)
            detalhe_fundo(symbol)

            time.sleep(0.5)
    

def detalhe_fundo(fundo):
    pagina_detalhe = requests.get(URL_BASE + "/" + fundo)
    soup = BeautifulSoup(pagina_detalhe.content, 'html.parser')
    liquidez_diaria = soup.find_all("span", class_="indicator-value")[0].get_text(strip=True)
    ultimo_rendimento = soup.find_all("span", class_="indicator-value")[1].get_text(strip=True)
    
    dividend_yield = soup.find_all("span", class_="indicator-value")[2].get_text(strip=True)
    patrimonio_liquido = soup.find_all("span", class_="indicator-value")[3].get_text(strip=True)
    valor_patrimonal = soup.find_all("span", class_="indicator-value")[4].get_text(strip=True)
    rentabilidade_mes = soup.find_all("span", class_="indicator-value")[5].get_text(strip=True)
    pvp = soup.find_all("span", class_="indicator-value")[6].get_text(strip=True)
    
    print('\tLiquidez: ' + liquidez_diaria)
    print('\tRendimento: ' + ultimo_rendimento)
    print('\tDY: ' + dividend_yield)
    print('\tPatrimônio Liquido: ' + patrimonio_liquido)
    print('\tValor Patrimonial: ' + valor_patrimonal)
    print('\tRentabilidade/Mês: ' + rentabilidade_mes)
    print('\tP/VP: ' + pvp)

#detalhe_fundo("ABCP11")
obtem_fundos()