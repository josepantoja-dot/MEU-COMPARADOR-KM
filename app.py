import streamlit as st
import pandas as pd

# 1. Configurações da Página
st.set_page_config(
    page_title="Frota Inteligente | Comparador KM",
    page_icon="🚛",
    layout="wide"
)

# 2. CSS Blindado (Fundo Escuro, Bordas Pretas e Cabeçalho Branco Forte)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    
    /* Cards de métricas */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stMetricValue"] > div { color: #38bdf8 !important; }
    div[data-testid="stMetricLabel"] > label { color: #ffffff !important; font-weight: bold; }

    /* Estilo do Cabeçalho da Tabela (Nomes das Colunas) */
    thead tr th {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        border: 1px solid #000000 !important;
    }

    /* Estilo Geral da Tabela para aceitar bordas */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        padding: 2px;
    }
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
    st.caption("Versão 9.0 - Grid & High White Header")

# 4. Cabeçalho
st.title("🚛 Dashboard: Comparativo de Rodagem")

# 5. Área de Upload
c1, c2 = st.columns(2)
with c1:
    file_passado = st.file_uploader("📂 Planilha ANTERIOR", type=['csv', 'xlsx'], key="passado")
with c2:
    file_presente = st.file_uploader("📂 Planilha ATUAL", type=['csv', 'xlsx'], key="presente")

if file_passado and file_presente:
    try:
        def carregar(file):
            return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        df_a = carregar(file_passado)
        df_b = carregar(file_presente)

        if col_ponto in df_a.columns:
            df_a[col_ponto] = df_a[col_ponto].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        df_a_clean = df_a[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto', col_placa: 'Placa'})
        df_b_clean = df_b[[col_placa, col_km]].rename(columns={col_km: 'Atual', col_placa: 'Placa'})
        
        df_res = pd.merge(df_b_clean, df_a_clean, on='Placa', how='inner')
        
        for c in ['Anterior', 'Atual']:
            df_res[c] = pd.to_numeric(df_res[c], errors='coerce').fillna(0).astype(int)
            
        df_res['Diferença (KM)'] = df_res['Atual'] - df_res['Anterior']

        # Métricas
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Veículos", len(df_res))
        m2.metric("Total KM", f"{df_res['Diferença (KM)'].sum():,.0f}")
        m3.metric("Média", f"{df_res['Diferença (KM)'].mean():.1f}")
        m4.metric("Máximo", f"{df_res['Diferença (KM)'].max()}")

        # 6. Tabela com BORDAS PRETAS VERTICAIS
        st.markdown("### 📋 Relatório Detalhado")
        
        lista_cores = ['#D1E9FF', '#D1FFD6', '#FFE4D1', '#FFF9D1']

        def aplicar_estilo_grid(row):
            cor_fundo = lista_cores[int(row.name) % len(lista_cores)]
            # Adicionado border-left e border-right para separar as colunas com preto puro
            return [f'background-color: {cor_fundo}; color: #000000; font-weight: bold; border: 1.5px solid #000000'] * len(row)

        def style_diferenca_grid(val):
            color = '#E60000' if val < 0 else '#006400' 
            # A coluna de diferença também mantém a borda preta
            return f'color: {color}; font-weight: 900; font-size: 18px; border: 1.5px solid #000000'

        df_style = df_res[['Placa', 'Ponto', 'Anterior', 'Atual', 'Diferença (KM)']].style \
            .apply(aplicar_estilo_grid, axis=1) \
            .map(style_diferenca_grid, subset=['Diferença (KM)'])

        st.dataframe(df_style, use_container_width=True, height=600)
        
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 BAIXAR RELATÓRIO", csv, "relatorio_grid.csv", "text/csv", use_container_width=True)

    except Exception as e:
        st.error(f"Erro: {e}")
