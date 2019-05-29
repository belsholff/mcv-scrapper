#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import re
import time
from time import localtime, strftime
from robobrowser import RoboBrowser

######### LOGIN #########
def login_mcv(browser, URI, CPF, DNasc):
    browser.open(URI)
    if browser.url != URI:
        error_log = open('error.log', 'a')
        error_log.writelines('[ '+ strftime("%Y-%m-%d | %H:%M:%S -0300", localtime()) + " ] ¬¬ Página de login por CPF não disponível.\n")
        error_log.close()
        return browser

    #lembrando que o token do cookie não é igual ao encontrado na DOM
    token0 = browser.find(attrs={'name':'__RequestVerificationToken'})['value']
    #token do cookie
    # token1 = browser.session.cookies['__RequestVerificationToken_L1JlZGUuQmVtLkVzdGFy0']

    form = browser.get_form()
    form['CPF'] = CPF
    form['DataNascimento'] = DNasc
    form['__RequestVerificationToken'] = token0
    browser.submit_form(form)
    return browser

######### BUSCANDO ESPECIALIDADES #########
def busca_especialidades(browser, URL):
    lista_especialidades = {}
    for a_tag in browser.find_all(attrs={'class': 'btn btn-primary btn-lg'}):
        especialidade = a_tag.text.encode('utf-8')
        # print especialidade

        #coletando apenas o primeiro procedimento de cada especialidade.
        proc_tag = a_tag.find_next('a')
        lista_especialidades[especialidade] = {'procedimento': proc_tag.text.encode('utf-8'), 'link': (URL + proc_tag['href']).encode('utf-8')}

    return lista_especialidades

######### SELECIONANDO ESPECIALIDADE E CONSTRUÍNDO LISTA DE VAGAS #########

def coleta_vagas(browser, lista_especialidades, esp):
    browser.open(lista_especialidades[esp]['link']) #lança exceção se o site não abrir
    if browser.url == lista_especialidades[esp]['link']:
        lista_vagas = []
        for item in browser.find_all('h4'):
            nome_medico = item.contents[1].text.encode('utf-8')
            # print nome_medico
            tag = item.next_sibling.next_sibling
            if tag.name == 'div':
                lista_vagas.append({'nome': nome_medico, 'vagas': 0})
            elif tag.name == 'span':
                lista_vagas.append({'nome': nome_medico, 'vagas': int(tag.text.split()[0])})
            else:
                error_log = open('error.log', 'a')
                error_log.writelines('[ '+ strftime("%Y-%m-%d | %H:%M:%S -0300", localtime()) + " ] ¬¬ Erro: possivelmente alguma estrutura do site mudou.\n")
                error_log.close()
                return lista_vagas

    return lista_vagas

######### FORMATA E ENVIA MENSAGEM PELO TELEGRAM #########
def envia_telegram(browser, lista, esp, token, chatID):
    string = "||||| " + esp + " |||||\n" + strftime("||||| %a, %d %b %Y %H:%M:%S", localtime()) + ' |||||\n'
    for item in lista:
        string += (item['nome'] + " -> " + str(item['vagas']) + " vagas;\n")

    browser.open('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatID + '&text=' + string)

def main():

    ######### MACROS #########
    nCPF = sys.argv[1]
    nDNASC = sys.argv[2]
    entrada_especialidade = sys.argv[3]
    URI_login = 'https://minhaconsulta.vitoria.es.gov.br/Rede.Bem.Estar/Agendamento/CPF-Data-Nascimento'
    URL = 'https://minhaconsulta.vitoria.es.gov.br'
    TOKEN_BOT_TELEGRAM = '709313251:AAEImyGQubUuqe-Eq0tBi9W5rxRDjSEUsG8' #trocar para cada usuário do script
    CHAT_ID = "25263053" #trocar para cada usuário do script
    INT_ATUALIZACAO = int(sys.argv[4])

    while True:

        browser = RoboBrowser(parser='lxml', history=True, user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0.4) Gecko/20100101 Firefox/66.0')

        browser = login_mcv(browser, URI_login, nCPF, nDNASC)
        if browser.url == 'https://minhaconsulta.vitoria.es.gov.br/Rede.Bem.Estar/Agendamento/Lista-Consultas':
            lista_especialidades = busca_especialidades(browser, URL)
            if len(lista_especialidades) != 0:
                listao = coleta_vagas(browser, lista_especialidades, entrada_especialidade)
                ######### SE O NUM DE VAGAS FOR MAIOR QUE 0, ENVIA PRO TELEGRAM #########
                num_vagas = 0
                for item in listao:
                    num_vagas += item['vagas']

                if num_vagas != 0:
                    envia_telegram(browser, listao, entrada_especialidade, TOKEN_BOT_TELEGRAM, CHAT_ID)

        time.sleep(INT_ATUALIZACAO) #executa a cada INT_ATUALIZACAO segundos

if __name__ == '__main__':
    main()
