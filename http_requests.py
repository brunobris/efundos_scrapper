import requests, time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def requests_retry_session(retries=3, backoff_factor=0.5, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def http_get(url):
    return requests_retry_session().get(url, timeout=10, verify=False)

# try:
#     teste = http_get('http://httpbin.org/status/500')
#     print(teste.status_code)
#     print('SUCESSO')
# except Exception as e:
#     print('ERROO {}'.format(e)) 