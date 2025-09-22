# -*- coding: utf-8 -*-

# ===================================================================================
#   SIMULADOR DE ACESSO À API DA ZENTRA CLOUD (VERSÃO 4.0 - PRONTO PARA NUVEM)
#
#   - Adaptado para rodar como um serviço contínuo (worker) em plataformas como Render.
#   - Remove interatividade do usuário (inputs) e limpeza de tela.
#   - Imprime logs diretamente no console, que serão capturados pelo serviço de nuvem.
# ===================================================================================

import random
from datetime import datetime
import pandas as pd
import time
import os # Mantemos 'os' por enquanto, mas não para limpar a tela

# --- FUNÇÃO QUE SIMULA A RESPOSTA DA API ---
def simular_chamada_api_zentra(api_token, device_id):
    """
    Simula uma chamada de API retornando uma estrutura JSON complexa.
    """
    if not api_token or not device_id:
        return {'sucesso': False, 'mensagem': 'Token ou ID do dispositivo não fornecido.'}

    timestamp_iso = datetime.now().isoformat(timespec='seconds') + "Z"
    umidade = round(random.uniform(34.5, 35.5) + random.uniform(-0.5, 0.5), 2)
    temp_solo = round(random.uniform(19.0, 21.0) + random.uniform(-0.2, 0.2), 2)
    precipitacao = round(random.uniform(0.0, 0.5), 2) if random.random() > 0.8 else 0.0

    resposta_simulada = {
        'sucesso': True,
        'dados': {
            'leituras': [{
                'timestamp': timestamp_iso,
                'dispositivo_id': device_id,
                'medicoes': {
                    'umidade_solo_percentual': umidade,
                    'temperatura_solo_celsius': temp_solo,
                    'precipitacao_mm': precipitacao
                }
            }]
        }
    }
    return resposta_simulada

# ===================================================================================
# --- INÍCIO DA EXECUÇÃO DO PROGRAMA ---
# ===================================================================================

# --- PASSO 1: CONFIGURAÇÃO (Valores fixos para o ambiente de nuvem) ---
# Em um projeto real, estes valores viriam de Variáveis de Ambiente
API_TOKEN = "zcl_auth_exemplo_token_para_nuvem"
DEVICE_ID = "SN-A7B4-C2D9"
INTERVALO_SEGUNDOS = 15 # Aumentamos o intervalo para não sobrecarregar o log

print("===================================================")
print("     INICIANDO SIMULADOR DE MONITORAMENTO ZENTRA     ")
print(f"     Dispositivo: {DEVICE_ID}")
print("===================================================")
time.sleep(2)

dados_processados = []

# --- PASSO 2: LOOP DE MONITORAMENTO CONTÍNUO ---
# Usamos 'try/except' para garantir que o programa termine de forma limpa se for interrompido
try:
    while True:
        # 2.1: Chama a nossa função que simula a API
        resposta_api = simular_chamada_api_zentra(API_TOKEN, DEVICE_ID)

        # 2.2: Processa a resposta
        if resposta_api and resposta_api.get('sucesso'):
            leituras_atuais = resposta_api['dados']['leituras']

            # 2.3: "Achata" os dados para um formato tabular
            for leitura in leituras_atuais:
                leitura_plana = {
                    "Horário": leitura['timestamp'],
                    "Umidade (%)": leitura['medicoes']['umidade_solo_percentual'],
                    "Temp. Solo (°C)": leitura['medicoes']['temperatura_solo_celsius'],
                    "Chuva (mm)": leitura['medicoes']['precipitacao_mm']
                }
                # Em vez de construir uma tabela gigante, vamos apenas imprimir a última leitura.
                # Isso é muito mais eficiente para um serviço de log.
                print(f"Nova Leitura: {leitura_plana}")

        else:
            print(f"[ERRO] Não foi possível obter os dados: {resposta_api.get('mensagem', 'Erro desconhecido')}")

        # 2.4: Pausa antes da próxima chamada
        # A função print() com flush=True força a saída imediata do texto, o que é bom para logs.
        print(f"--- Próxima verificação em {INTERVALO_SEGUNDOS} segundos ---", flush=True)
        time.sleep(INTERVALO_SEGUNDOS)

except KeyboardInterrupt:
    print("\n===================================================")
    print("      Serviço interrompido. Finalizando...      ")
    print("===================================================")