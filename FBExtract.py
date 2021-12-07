from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import getpass
import time
import csv

def rolar_fim_pagina(nav):

    #Subrotina que faz a rolagem da página de pesquisa de vídeos até o final, afim de carregar todos os vídeos disponíveis daquela pesquisa

    fim = False
    while fim is False: #rola até o final da página (fim dos resultados da pesquisa)
        try:
            nav.find_element_by_xpath('//*[text()="Fim dos resultados"]')
            fim = True
        except:
            nav.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(2)

def login(nav, l, s):

    #Subrotina que abre a página de login do facebook e entra com os dados oferecidos pelo usuário

    n.get('https://facebook.com/login.php')

    nav.find_element_by_xpath('//*[@id="email"]').send_keys(l)
    nav.find_element_by_xpath('//*[@id="pass"]').send_keys(s)
    nav.find_element_by_xpath('//*[@id="pass"]').send_keys(Keys.ENTER)

    time.sleep(5)

def id_usuario(nav):

    #Subrotina utilizada para pegar o número de ID do usuário logado

    nav.get('https://facebook.com/profile')
    time.sleep(5)
    id_perfil = nav.current_url.split('?id=')[1]
    return id_perfil

def limpa_historico(nav, id):

    #Subrotina utilizada para a limpeza do histórico de visualização de vídeos a cada vídeo aberto

    nav.switch_to_window(n.window_handles[1]) #vai para a nova aba
    nav.get('https://facebook.com/' + id + '/allactivity?activity_history=false&category_key=SEARCH&manage_mode=false')
    time.sleep(3)
    nav.find_element_by_xpath('//*[text()="Limpar pesquisas"]').click() #limpa o histórico de pesquisas
    time.sleep(2)
    nav.get('https://facebook.com/' + id + '/allactivity?activity_history=false&category_key=VIDEOWATCH&manage_mode=false')
    time.sleep(3)
    nav.find_element_by_xpath('//*[text()="Limpar histórico de vídeos assistidos"]').click()
    time.sleep(2)
    try:
        nav.find_element_by_xpath('//*[text()="Clear Video Watch History"]').click()
        time.sleep(2)
        nav.switch_to_window(n.window_handles[0]) #volta pra a primeira aba
    except:
        nav.switch_to_window(n.window_handles[0])
    time.sleep(2)

def testa_link(nav, l):

    #Subrotina utilizada quando era necessário fazer o teste de um link em específico, no caso de não ser possível a abertura do vídeo
    #Esta subrotina não é utilizada na versão atual do código

    nav.execute_script('window.open();') #abre outra nova aba, para executar os testes de página deletada
    time.sleep(3)
    nav.switch_to_window(n.window_handles[2])
    nav.get(l)
    time.sleep(3)
    try:
        nav.find_element_by_xpath('//*[text()=Esta Página não está disponível no momento').click()
        nav.execute_script('window.close();')
        time.sleep(2)
        nav.switch_to_window(n.window_handles[0])
        return False
    except:
        ActionChains(n).send_keys(Keys.SPACE).perform() #aperta barra de espaço para pausar o vídeo
        time.sleep(2)
        nav.switch_to_window(n.window_handles[0])
        return True

print('Login: ')
usuario = input()
senha = getpass.getpass('Senha (insira a senha e pressione Enter): ')
print('Termo de pesquisa: ')
termo = input()

print('\nProcessando...\n')

n = webdriver.Firefox()

login(n, usuario, senha) #faz login no Facebook com o usuário e senha informados

id_perfil = id_usuario(n) #armazena o ID de perfil do usuário na variável id_perfil

n.execute_script('window.open();') #abre nova aba, pra deixar aberto o histórico e ir apagando (pesquisas e vídeos assistidos)
time.sleep(3)

limpa_historico(n, id_perfil) #faz a limpeza de histórico pré-pesquisa

l = ('https://www.facebook.com/watch/search/?q=' + termo)

n.get(l)
time.sleep(3)

rolar_fim_pagina(n)

linksgeral = n.find_elements_by_xpath('//a') #pega todos os elementos de vídeo clicaveis na página

totalVideos = sum('/videos/' in s.get_attribute('href') for s in linksgeral) #verifica quantos são os vídeos de fato e informa ao usuário

print('Extração de vídeos de pesquisa concluída. Total de vídeos de pesquisa: ' + str(totalVideos))
print('\nIniciando extração de vídeos a seguir...')

cont = 1

with open(termo + ' - Pesquisa' + '.csv', 'w', newline='') as csvfile: #gera o arquivo para os vídeos da pesquisa
    with open(termo + ' - A Seguir' + '.csv', 'w', newline='') as csvfile2: #gera o arquivo para os vídeos relacionados

        fieldnames = ['class', 'id_pagina', 'id_video', 'link'] #pesquisa
        fieldnames2 = ['class', 'id_pagina', 'id_video', 'link', 'link_origem'] #relacionados
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer2 = csv.DictWriter(csvfile2, fieldnames=fieldnames2)

        writer.writeheader()
        writer2.writeheader()

        for l in linksgeral:

            link = l.get_attribute('href')

            if('/videos/' in link):

                print('Extraindo vídeos a seguir (' + str(cont) + '/' + str(totalVideos) + ')')

                n.execute_script('arguments[0].scrollIntoView();', l) #coloca o elemento do vídeo na tela
                time.sleep(5)
                ActionChains(n).move_to_element_with_offset(l, l.size['width']-10, l.size['height']-10).click().perform() #clica em um espaço que irá cair sempre no vídeo e não na página
                time.sleep(5)

                ids = link.split('/')
                id_pagina = ids[3]
                id_video = ids[5]
                writer.writerow({'class': '0', 'id_pagina': id_pagina, 'id_video': id_video, 'link': link})

                #Com o vídeo aberto, são extraídos os vídeos a seguir:

                if('/videos/' in n.current_url): #Etapa de segurança para assegurar que um vídeo foi aberto

                    ActionChains(n).send_keys(Keys.SPACE).perform() #Aperta barra de espaço para pausar o vídeo
                    time.sleep(2)
                    n.find_element_by_xpath('//*[text() = "Mais como esse"]').click() #Clica no "Mais como esse, para exibir os vídeos a seguir"
                    time.sleep(3)
                    rels = n.find_elements_by_xpath('//a') #Encontra os vídeos a seguir na página daquele vídeo

                    for r in rels: #Insere as entradas na tabela de vídeos a seguir

                        linkrel = r.get_attribute('href')

                        if('__cft__' in linkrel):
                            ids2 = linkrel.split('/')
                            id_pagina2 = ids2[3]
                            id_video2 = ids2[5].split('?')[0]
                            writer2.writerow({'class': '0', 'id_pagina': id_pagina2, 'id_video': id_video2, 'link': linkrel, 'link_origem': link})

                    n.back() #Retorna para a página de pesquisa
                    time.sleep(4)

                try:
                    n.find_element_by_xpath('//div[@aria-label="Fechar modo Assistir e rolar"]').click() #Fecha o vídeo em pop-up
                    time.sleep(2)
                    limpa_historico(n, id_perfil) #Limpa o histórico de visualização a cada vídeo, caso seja um vídeo curto e conte como visto
                except:
                    time.sleep(1)

                cont = cont + 1
