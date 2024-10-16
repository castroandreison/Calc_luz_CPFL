import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Função para carregar a última leitura salva de um arquivo
def carregar_ultima_leitura():
    try:
        with open('ultima_leitura.txt', 'r') as file:
            ultima_leitura = float(file.read().strip())
        return ultima_leitura
    except FileNotFoundError:
        return 10334.65  # Valor inicial de exemplo

# Função para salvar a nova leitura no arquivo
def salvar_ultima_leitura(leitura_atual):
    with open('ultima_leitura.txt', 'w') as file:
        file.write(str(leitura_atual))

# Função para calcular o consumo
def calcular_consumo(leitura_anterior, leitura_atual, tarifa_te, tarifa_tusd, parte_salao):
    dif_kwh = leitura_atual - leitura_anterior
    valor_te = dif_kwh * tarifa_te
    valor_tusd = dif_kwh * tarifa_tusd
    valor_total = (valor_te + valor_tusd) * 1
    return dif_kwh, valor_te, valor_tusd, valor_total

# Função para salvar o histórico em um arquivo Excel
def salvar_historico(df, historico_file):
    df.to_excel(historico_file, index=False)

# Função para ler o histórico do arquivo Excel
def ler_historico(historico_file):
    if os.path.exists(historico_file):
        return pd.read_excel(historico_file)
    return pd.DataFrame(columns=['Data', 'Valor da leitura', 'Dif(kWh)', 'TE Total (R$)', 'TUSD Total (R$)', 'Valor total (R$)'])

# Configurando a interface Streamlit
st.title("Cálculo de Consumo de Energia - Sala Comercial")

# Carrega a última leitura salva
ultima_leitura = carregar_ultima_leitura()

# Campo para inserção da leitura anterior
leitura_anterior = st.number_input("Leitura Anterior:", value=ultima_leitura, format="%.2f", step=0.01)

# Campo para inserção da nova leitura atual
leitura_atual = st.number_input("Leitura Atual:", value=ultima_leitura, format="%.2f", step=0.01)

# Campos de tarifa TE e TUSD com valores iniciais
tarifa_te = st.number_input("Tarifa TE (R$):", value=0.37361703, format="%.6f", step=0.000001)
tarifa_tusd = st.number_input("Tarifa TUSD (R$):", value=0.55196809, format="%.6f", step=0.000001)

# Botão de calcular
if st.button("Calcular"):
    # Faz o cálculo do consumo
    dif_kwh, valor_te, valor_tusd, valor_total = calcular_consumo(leitura_anterior, leitura_atual, tarifa_te, tarifa_tusd, 0.8141)

    # Exibe o resultado na interface
    st.write(f"Diferença de kWh: {dif_kwh:.2f}")
    st.write(f"TE Total (R$): {valor_te:.2f}")
    st.write(f"TUSD Total (R$): {valor_tusd:.2f}")
    st.write(f"Valor total (R$): {valor_total:.2f}")

    # Atualiza e salva a última leitura
    salvar_ultima_leitura(leitura_atual)

    # Atualiza o histórico em um arquivo Excel
    data_atual = datetime.now().strftime('%d/%m/%Y')
    novo_dado = {
        'Data': [data_atual],
        'Valor da leitura': [leitura_atual],
        'Dif(kWh)': [dif_kwh],
        'TE Total (R$)': [valor_te],
        'TUSD Total (R$)': [valor_tusd],
        'Valor total (R$)': [valor_total]
    }
    df = pd.DataFrame(novo_dado)

    # Lê o histórico existente e atualiza
    historico_file = 'historico_consumo_sala_comercial.xlsx'
    historico_df = ler_historico(historico_file)
    historico_df = pd.concat([historico_df, df], ignore_index=True)

    # Salva o histórico atualizado em um arquivo Excel
    salvar_historico(historico_df, historico_file)

    # Mensagem de sucesso
    st.success("Cálculo realizado e dados salvos com sucesso!")

# Botão para exportar dados
if st.button("Exportar Dados"):
    # Lê o histórico existente
    historico_df = ler_historico('historico_consumo_sala_comercial.xlsx')
    
    # Salva o histórico em um objeto BytesIO para download
    excel_file = 'historico_consumo_sala_comercial.xlsx'
    salvar_historico(historico_df, excel_file)
    
    # Cria o botão de download
    with open(excel_file, "rb") as f:
        st.download_button(
            label="Baixar Histórico de Consumo",
            data=f,
            file_name=excel_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
