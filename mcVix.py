import sys
import re
from robobrowser import RoboBrowser

######### MACROS #########

#Explicar e validar entradas
CPF = sys.argv[1]
DNasc = sys.argv[2]
entrada_especialidade = sys.argv[3]
URI_login = 'https://minhaconsulta.vitoria.es.gov.br/Rede.Bem.Estar/Agendamento/CPF-Data-Nascimento'
URL = 'https://minhaconsulta.vitoria.es.gov.br'

######### LOGIN #########

browser = RoboBrowser(parser='lxml', history=True, user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0.4) Gecko/20100101 Firefox/66.0 ')
browser.open(URI_login)

#token do cookie não casa com o encontrado na DOM
token0 = browser.find(attrs={'name':'__RequestVerificationToken'})['value']

#token do cookie
# token1 = browser.session.cookies['__RequestVerificationToken_L1JlZGUuQmVtLkVzdGFy0']

form = browser.get_form()
form['CPF'] = CPF
form['DataNascimento'] = DNasc
form['__RequestVerificationToken'] = token0
browser.submit_form(form)

######### BUSCANDO ESPECIALIDADES #########

lista_especialidades = {}
for a_tag in browser.find_all(attrs={'class': 'btn btn-primary btn-lg'}):
    especialidade = a_tag.text
    # print especialidade

    #coletando apenas o primeiro procedimento de cada especialidade.
    proc_tag = a_tag.find_next('a')
    lista_especialidades[especialidade] = {'procedimento': proc_tag.text, 'link': URL + proc_tag['href']}

# print lista_especialidades

######### SELECIONANDO ESPECIALIDADE #########

def clinico_case():
    browser.follow_link('lista_especialidades['Cl\xednico Geral']['link']')

def dentista_case():
    browser.follow_link('lista_especialidades['Dentista']['link']')

# def enfermeiro_case():
    # browser.follow_link('lista_especialidades['Enfermeiro']['link']')

# def psicologo_case():
    # browser.follow_link('lista_especialidades['Psic\xf3logo']['link']')

options = {'Cl\xednico Geral' : clinico_case,
           # 'Enfermeiro'       : enfermeiro_case,
           # 'Psic\xf3logo'     : psicologo_case,
           'Dentista'         : dentista_case
}

options[entrada_especialidade]()

# for item in browser.find_all(True):
# for item in browser.find_all(attrs={'class': 'col-md-3'}):
     # print item
