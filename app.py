import streamlit as st
import pandas as pd

# 1. Configurações da Página
st.set_page_config(page_title="Frota Pro", layout="wide")

# 2. CSS Blindado (Bordas Pretas e Cabeçalho Branco Forte)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    
    table {
        border-collapse: collapse !important;
        width: 100% !important;
        border: 2px solid #000000 !important;
        background-color: white !important;
    }

    th {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        text-align: center !important;
        border: 2px solid #000000 !important;
        padding: 10px !important;
    }

    td {
        border: 2px solid #000000 !important;
        padding: 8px !important;
        text-align: center !important;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.title("Configurações")
    col_placa = st.text_input("📝 Placa", "Placa")
    col_ponto = st.text_input("📍 Ponto", "Ponto de Medição")
    col_km = st.text_input("🔢 KM", "Odômetro (KM)")

st.title("🚛 Dashboard: Comparativo de Rodagem")

c1, c2 = st.columns(2)
with c1:
    file_passado = st.file_uploader("📂 Planilha ANTERIOR", type=['csv', 'xlsx'])
with c2:
    file_presente = st.file_uploader("📂 Planilha ATUAL", type=['csv', 'xlsx'])

if file_passado and file_presente:
    try:
        def carregar(file):
            return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        df_ant = carregar(file_passado)
        df_atu = carregar(file_presente)

        # --- LIMPEZA CRÍTICA DOS ZEROS NO PONTO ---
        if col_ponto in df_ant.columns:
            # Converte para string e remove o .000000
            df_ant[col_ponto] = df_ant[col_ponto].astype(str).str.replace(r'\.0+$', '', regex=True)

        # Preparação e Cruzamento
        df_atu_clean = df_atu[[col_placa, col_km]].rename(columns={col_km: 'Atual', col_placa: 'Placa'})
        df_ant_clean = df_ant[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto', col_placa: 'Placa'})
        
        df_res = pd.merge(df_atu_clean, df_ant_clean, on='Placa', how='inner')

        # Cálculos (convertendo KMs para inteiros)
        df_res['Anterior'] = pd.to_numeric(df_res['Anterior'], errors='coerce').fillna(0).astype(int)
        df_res['Atual'] = pd.to_numeric(df_res['Atual'], errors='coerce').fillna(0).astype(int)
        df_res['Diferença (KM)'] = df_res['Atual'] - df_res['Anterior']

        # 4. Estilização de Cores Vibrantes
        lista_cores = ['#D1E9FF', '#D1FFD6', '#FFE4D1', '#FFF9D1']

        def style_final(df):
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for i in range(len(df)):
                cor_fundo = lista_cores[i % len(lista_cores)]
                # Estilo das colunas normais
                styles.iloc[i, :-1] = f'background-color: {cor_fundo}; font-weight: bold;'
                
                # Estilo da coluna Diferença
                val = df.iloc[i]['Diferença (KM)']
                cor_texto = '#E60000' if val < 0 else '#006400'
                styles.iloc[i, -1] = f'background-color: {cor_fundo}; color: {cor_texto}; font-weight: 900; font-size: 18px;'
            return styles

        st.markdown("### 📋 Relatório Detalhado")
        
        # Seleciona colunas e aplica o estilo
        df_mostrar = df_res[['Placa', 'Ponto', 'Anterior', 'Atual', 'Diferença (KM)']]
        
        # st.table força a visualização HTML que mantém as bordas
        st.table(df_mostrar.style.apply(style_final, axis=None))

        # Download
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 BAIXAR RELATÓRIO", csv, "relatorio.csv", use_container_width=True)

    except Exception as e:
        st.error(f"Erro: {e}")
        
