from datetime import date, datetime
from dateutil import parser

#Converte padrão 01/10/2010 para 2010-10-01
#Se o dia não for especificado, 10/2020, converte para o primeiro dia do mês
def converter_data(data_string):
    return str(parser.parse(data_string, dayfirst=True, default=datetime(2020, 1, 1)))