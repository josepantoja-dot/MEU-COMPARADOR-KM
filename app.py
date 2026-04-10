import streamlit as st
import pandas as pd

# 1. Configurações da Página
st.set_page_config(
    page_title="Frota Inteligente | Comparador KM",
    page_icon="🚛",
    layout="wide"
)

# 2. Estilo CSS para o Dashboard (Fundo Escuro e Cards)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    [data-testid="stMetricValue"] > div { color: #38bdf8; }
    [data-testid="stMetricLabel"] > label { color: #94a3b8; }
    /* Estilização da área de upload */
    .stFileUploader { background-color: #1e293b; border-radius: 10px; padding: 10px; border: 1px dashed #38bdf8; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830305.png", width=100)
    st.title("Configurações")
    col_placa = st.text_input("📝 Nome da Coluna Placa", "Placa")
    col_ponto = st.text_input("📍 Nome da Coluna Ponto", "Ponto de Medição")
    col_km = st.text_input("🔢 Nome da Coluna KM", "Odômetro (KM)")
    st.divider()
    st.caption("Versão 5.0 - Multi-Cores Pro")

# 4. Cabeçalho Principal
st.title("🚛 Dashboard: Comparativo de Rodagem de Frota")
st.write("Análise automática e visual de variação de quilometragem")

# 5. Área de Upload
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 🕒 Planilha ANTERIOR")
    file_passado = st.file_uploader("Arraste o arquivo de ONTEM", type=['csv', 'xlsx'], key="passado")
with c2:
    st.markdown("### 🕒 Planilha ATUAL")
    file_presente = st.file_uploader("Arraste o arquivo de HOJE", type=['csv', 'xlsx'], key="presente")

if file_passado and file_presente:
    try:
        def carregar(file):
            return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        df_a = carregar(file_passado)
        df_b = carregar(file_presente)

        # Limpeza do Ponto (removendo .0)
        if col_ponto in df_a.columns:
            df_a[col_ponto] = df_a[col_ponto].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        df_a_clean = df_a[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto', col_placa: 'Placa'})
        df_b_clean =
