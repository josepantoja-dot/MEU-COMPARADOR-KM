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
    .stFileUploader { background-color: #1e293b; border-radius: 10px; padding: 10px; border: 1px dashed #38bdf8; }
    /* Estilo para garantir que o texto da tabela seja legível */
    [data-testid="stDataFrame"] { background-color: white; border-radius: 10px; }
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
    st.caption("Versão 5.1 - Fix Syntax Error")

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

# 6. Processamento
if file_passado and file_presente:
    try:
        def carregar(file):
            if file.name.endswith('.xlsx'):
                return pd.read_excel(file)
            return pd.read_csv(file)
        
        df_a = carregar(file_passado)
        df_b = carregar(file_presente)

        # Limpeza do Ponto
        if col_ponto in df_a.columns:
            df_a[col_ponto] = df_a[col_ponto].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        # Seleção das colunas (Garantindo que a linha não quebre)
        df_a_clean = df_a[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto', col_placa: 'Placa'})
        df_b_clean = df_b[[col_placa, col_km]].rename(columns={col_km: 'Atual', col_placa: 'Placa'})
        
        # Cruzamento
        df_res = pd.merge(df_b_clean, df_a_clean, on='Placa', how='inner')
        
        # Conversão numérica
        for c in ['Anterior', 'Atual']:
            df_res[c] = pd.to_numeric(df_res[c], errors='coerce').fillna(0).astype(int)
            
        df_res['Diferença (KM)'] = df_res['Atual'] - df_res['Anterior']

        # Cards de Métricas
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Veículos", len(df_res))
        m2.metric("Total KM", f"{df_res['Diferença (KM)'].sum():,.0f}")
        m3.metric("Média", f"{df_res['Diferença (KM)'].mean():.1f}")
        m4.metric("Máximo", f"{df_res['Diferença (KM)'].max()}")

        # 7. Exibição da Tabela Multi-Cores
        st.markdown("### 📋 Relatório Detalhado")
        
        # Lista de 4 cores pastéis para alternar
        lista_cores = ['#ffffff', '#f0f9ff', '#f0fdf4', '#fff7ed']

        def style_rows(df):
            # Cria uma matriz de estilos com o mesmo tamanho do DataFrame
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for i in range(len(df)):
                cor = lista_cores[i % len(lista_cores)]
                styles.iloc[i, :] = f'background-color: {cor}'
            return styles

        def style_diff(val):
            color = '#ef4444' if val < 0 else '#22c55e'
            return f'color: {color}; font-weight: bold'

        # Aplicar estilo zebra e cor de texto na diferença
        styled_df = df_res[['Placa', 'Ponto', 'Anterior', 'Atual', 'Diferença (KM)']].style \
            .apply(style_rows, axis=None) \
            .map(style_diff, subset=['Diferença (KM)'])

        st.dataframe(styled_df, use_container_width=True, height=500)

        # Botão de Download
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 BAIXAR RELATÓRIO", csv, "relatorio.csv", "text/csv", use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Erro ao processar. Certifique-se que as colunas '{col_placa}' e '{col_km}' existem nas planilhas.")
