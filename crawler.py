import re
import threading
from queue import Queue
import requests
from bs4 import BeautifulSoup

from links import LINK_DOMINIO, LINK_URL_AUTOMOVEIS

LINKS = Queue()
TELEFONES = []

DOMINIO = LINK_DOMINIO
URL_AUTOMOVEIS = LINK_URL_AUTOMOVEIS

def requisicao(url):
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
              return resposta.text
        else:
            print('Erro ao fazer reqiuisição')
    except Exception as error:
        print('Erro ao fazer requisição')
        print(error)

def parsing(resposta_html):
    try:
        soup = BeautifulSoup(resposta_html, 'html.parser')
        return soup
    except Exception as error:
        print('Erro ao fazer o parsing html')
        print(error)


def encontrar_links(soup):
    try:
        cards_pai = soup.find("div", class_="ui three doubling link cards")
        cards = cards_pai.find_all('a')
    except:
        print('erro ao enconttrar links')
        return None
    links = []
    for card in cards:
        try:
            link = card['href']
            links.append(link)
        except:
            pass

    return links

def encontrar_telefones(soup):
    try:
        descricao = soup.find_all("div", class_="sixteen wide column")[2].p.get_text().strip()
        regex = re.findall(r"\(?0?\d{2}\)?[-.\s]?9\d{0,1}[-.\s]?\d{4}[-.\s]?\d{4}|0?\d{2}[-]9\d{8}", descricao)
        return regex
    except Exception as error:
        print('Erro ao encontrar descrição:', error)
        return []

print_lock = threading.Lock()

def descobrir_telefones():
    while not LINKS.empty():
        try:
            link_anuncio = LINKS.get()
        except:
            return

        resposta_anuncio = requisicao(DOMINIO + link_anuncio)

        if resposta_anuncio:
            soup_anuncio = parsing(resposta_anuncio)
            if soup_anuncio:
               telefones = encontrar_telefones(soup_anuncio)
               for telefone in telefones:
                   if telefone.strip():
                      with print_lock:
                         print('telefone encontrado:', telefone.strip())
                      TELEFONES.append(telefone.strip())
                      salvar_telefone(telefone.strip())

def salvar_telefone(telefone):
    try:
        with open('telefones.csv', 'a', encoding='utf-8') as arquivo:
            arquivo.write(telefone + '\n')
    except Exception as error:
        print('Erro ao salvar telefone:', error)


if __name__ == '__main__':
    resposta_busca = requisicao(URL_AUTOMOVEIS)
    if resposta_busca:
        soup_busca = parsing(resposta_busca)
        if soup_busca:
            links = encontrar_links(soup_busca)
            if links:
                for link in links:
                    LINKS.put(link)

            THREADS = []
            for _ in range(10):
                t = threading.Thread(target=descobrir_telefones)
                THREADS.append(t)
                t.start()

            for t in THREADS:
                  t.join()

            print('\nTodos os telefones encontrados:')
            for telefone in TELEFONES:
                print(telefone)

