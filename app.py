import streamlit as st
import pandas as pd

# 1. Configurações da Página
st.set_page_config(page_title="Frota Pro", layout="wide")

# 2. CSS Blindado (Ataca diretamente a estrutura HTML da tabela)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    
    /* Estilo da Tabela Estática (st.table) */
    table {
        border-collapse: collapse !important;
        width: 100% !important;
        border: 2px solid #000000 !important;
        background-color: white !important;
    }

    /* Cabeçalho: Fundo preto, texto branco extra forte e bordas pretas */
    th {
        background-color: #000000 !important;
        color: #ffffff !important;
        font-weight: 900 !important;
        font-size: 18px !important;
        text-align: center !important;
        border: 2px solid #000000 !important;
        padding: 10px !important;
    }

    /* Células: Garante a borda preta em volta de cada dado */
    td {
        border: 2px solid #000000 !important;
        padding: 8px !important;
        text-align: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar e Uploads (Mantidos)
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
        
        df_res = pd.merge(
            carregar(file_presente)[[col_placa, col_km]].rename(columns={col_km: 'Atual', col_placa: 'Placa'}),
            carregar(file_passado)[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto', col_placa: 'Placa'}),
            on='Placa'
        )

        df_res['Diferença (KM)'] = df_res['Atual'].astype(int) - df_res['Anterior'].astype(int)

        # 4. Estilização de Cores Vibrantes e Texto
        lista_cores = ['#D1E9FF', '#D1FFD6', '#FFE4D1', '#FFF9D1']

        def style_final(df):
            # Cria um DataFrame de estilos
            styles = pd.DataFrame('', index=df.index, columns=df.columns)
            for i in range(len(df)):
                cor_fundo = lista_cores[i % len(lista_cores)]
                # Aplica cor de fundo e texto preto para as primeiras colunas
                styles.iloc[i, :-1] = f'background-color: {cor_fundo}; color: #000000; font-weight: bold;'
                
                # Lógica da coluna Diferença
                val = df.iloc[i]['Diferença (KM)']
                cor_texto = '#E60000' if val < 0 else '#006400'
                styles.iloc[i, -1] = f'background-color: {cor_fundo}; color: {cor_texto}; font-weight: 900; font-size: 18px;'
            return styles

        # Exibição com st.table (que respeita as bordas HTML)
        st.markdown("### 📋 Relatório Detalhado")
        
        df_mostrar = df_res[['Placa', 'Ponto', 'Anterior', 'Atual', 'Diferença (KM)']]
        st.table(df_mostrar.style.apply(style_final, axis=None))

        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 BAIXAR RELATÓRIO", csv, "relatorio.csv", use_container_width=True)

    except Exception as e:
        st.error(f"Erro: {e}")
