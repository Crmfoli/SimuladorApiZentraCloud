# -*- coding: utf-8 -*-

# ===================================================================================
#   SIMULADOR DE ACESSO À API (VERSÃO 5.0 - WEB SERVICE COM FLASK)
#
#   - Adaptado para rodar no plano gratuito de Web Service do Render.
#   - Usa Flask para criar um endpoint web que responde aos health checks.
#   - A lógica da simulação roda em uma thread separada para não bloquear o servidor.
# ===================================================================================

import random
from datetime import datetime
import time
import threading  # Importa a biblioteca para trabalhar com threads
from flask import Flask  # Importa o Flask

# --- PARTE 1: APLICAÇÃO WEB (FLASK) ---

# Cria a aplicação web. O Render vai interagir com este objeto 'app'.
app = Flask(__name__)

@app.route('/')
def index():
    """Esta é a página principal do nosso serviço web."""
    # Ela apenas retorna uma mensagem simples para mostrar que o serviço está no ar.
    # É essa resposta que satisfaz os "health checks" do Render.
    return "Simulador Zentra está no ar. Verifique os logs para ver os dados."

# --- PARTE 2: LÓGICA DA SIMULAÇÃO ---

def simular_chamada_api_zentra(api_token, device_id):
    """Função que gera os dados simulados (sem alterações)."""
    timestamp_iso = datetime.now().isoformat(timespec='seconds') + "Z"
    umidade = round(random.uniform(34.5, 35.5) + random.uniform(-0.5, 0.5), 2)
    temp_solo = round(random.uniform(19.0, 21.0) + random.uniform(-0.2, 0.2), 2)
    precipitacao = round(random.uniform(0.0, 0.5), 2) if random.random() > 0.8 else 0.0

    resposta_simulada = {
        'sucesso': True,
        'dados': {
            'leituras': [{'timestamp': timestamp_iso, 'dispositivo_id': device_id,
                          'medicoes': {'umidade_solo_percentual': umidade,
                                       'temperatura_solo_celsius': temp_solo,
                                       'precipitacao_mm': precipitacao}}]
        }
    }
    return resposta_simulada

def rodar_simulador():
    """
    Esta função contém o loop infinito da nossa simulação.
    Ela será executada em segundo plano (em uma thread separada).
    """
    API_TOKEN = "zcl_auth_exemplo_token_para_nuvem"
    DEVICE_ID = "SN-A7B4-C2D9"
    INTERVALO_SEGUNDOS = 20 # Aumentamos um pouco o intervalo

    print("===================================================")
    print("     INICIANDO THREAD DE SIMULAÇÃO ZENTRA          ")
    print(f"     Dispositivo: {DEVICE_ID}")
    print("===================================================")
    time.sleep(2)

    while True:
        resposta_api = simular_chamada_api_zentra(API_TOKEN, DEVICE_ID)

        if resposta_api and resposta_api.get('sucesso'):
            leitura = resposta_api['dados']['leituras'][0]
            leitura_plana = {
                "Horário": leitura['timestamp'],
                "Umidade (%)": leitura['medicoes']['umidade_solo_percentual'],
                "Temp. Solo (°C)": leitura['medicoes']['temperatura_solo_celsius'],
                "Chuva (mm)": leitura['medicoes']['precipitacao_mm']
            }
            print(f"Nova Leitura: {leitura_plana}", flush=True)
        else:
            print(f"[ERRO] {resposta_api.get('mensagem', 'Erro desconhecido')}", flush=True)

        print(f"--- Próxima verificação em {INTERVALO_SEGUNDOS} segundos ---", flush=True)
        time.sleep(INTERVALO_SEGUNDOS)

# --- PARTE 3: INICIANDO TUDO ---

# Cria uma thread que irá executar a função 'rodar_simulador'.
# 'daemon=True' garante que a thread será encerrada quando o programa principal parar.
simulador_thread = threading.Thread(target=rodar_simulador, daemon=True)
simulador_thread.start() # Inicia a thread da simulação em segundo plano.

# O servidor Gunicorn do Render irá executar o objeto 'app' do Flask.
# O código acima será executado uma vez quando o servidor iniciar,
# lançando nossa simulação em paralelo.
