import streamlit as st
import pandas as pd

st.set_page_config(page_title="Comparador de KM", layout="wide")

st.title("📊 Comparador de Quilometragem")
st.markdown("Suba as planilhas para identificar o aumento de KM por ponto de medição.")

# --- CONFIGURAÇÃO DAS COLUNAS NA BARRA LATERAL ---
st.sidebar.header("⚙️ Nomes das Colunas")
st.sidebar.write("Ajuste se os nomes na sua planilha forem diferentes:")
col_placa = st.sidebar.text_input("Coluna da Placa", "Placa")
col_ponto = st.sidebar.text_input("Coluna do Ponto", "Ponto de Medicao")
col_km = st.sidebar.text_input("Coluna da KM", "Quilometragem")

# --- ÁREA DE UPLOAD ---
col1, col2 = st.columns(2)
with col1:
    file_passado = st.file_uploader("📂 Planilha DIA ANTERIOR", type=['csv', 'xlsx'])
with col2:
    file_presente = st.file_uploader("📂 Planilha DIA ATUAL", type=['csv', 'xlsx'])

# --- LÓGICA DE COMPARAÇÃO ---
if file_passado and file_presente:
    try:
        # Função para ler os arquivos corretamente
        def ler(file):
            if file.name.endswith('.csv'): return pd.read_csv(file)
            return pd.read_excel(file)

        df_a = ler(file_passado)
        df_b = ler(file_presente)

        # Seleciona e renomeia
        df_a = df_a[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'KM_Anterior', col_ponto: 'Ponto'})
        df_b = df_b[[col_placa, col_km]].rename(columns={col_km: 'KM_Atual'})

        # Cruza os dados
        df_final = pd.merge(df_b, df_a, on=col_placa, how='inner')
        df_final['Aumento_KM'] = df_final['KM_Atual'] - df_final['KM_Anterior']

        # Reordenar para visualização
        df_final = df_final[[col_placa, 'Ponto', 'KM_Anterior', 'KM_Atual', 'Aumento_KM']]

        st.divider()
        st.success("✅ Comparação realizada com sucesso!")

        # Tabela interativa
        st.dataframe(df_final, use_container_width=True)

        # Botão de download
        csv = df_final.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Resultado em Excel (CSV)", csv, "comparativo_km.csv", "text/csv")

    except Exception as e:
        st.error(f"⚠️ Erro ao processar: Verifique se os nomes das colunas '{col_placa}', '{col_km}' e '{col_ponto}' estão corretos na sua planilha.")
