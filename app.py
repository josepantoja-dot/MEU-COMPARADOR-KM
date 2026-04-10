import streamlit as st
import pandas as pd

# 1. Configurações da Página
st.set_page_config(
    page_title="Frota Inteligente | Comparador KM",
    page_icon="🚛",
    layout="wide"
)

# 2. Estilo CSS para melhorar o visual
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Configurações de Nomes)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830305.png", width=100)
    st.title("Configurações")
    st.info("Ajuste os nomes das colunas conforme sua planilha.")
    col_placa = st.text_input("📝 Nome da Coluna Placa", "Placa")
    col_ponto = st.text_input("📍 Nome da Coluna Ponto", "Ponto de Medição")
    col_km = st.text_input("🔢 Nome da Coluna KM", "Odômetro (KM)")
    st.divider()
    st.caption("Versão Final - Estabilizada")

# 4. Cabeçalho
st.title("🚛 Gestão de Frota: Comparativo de Rodagem")
st.subheader("Análise automática de variação de quilometragem")

# 5. Área de Upload
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 📅 Planilha DIA ANTERIOR")
    file_passado = st.file_uploader("Arraste o arquivo antigo aqui", type=['csv', 'xlsx'], key="passado")
with c2:
    st.markdown("### 📅 Planilha DIA ATUAL")
    file_presente = st.file_uploader("Arraste o arquivo novo aqui", type=['csv', 'xlsx'], key="presente")

# 6. Processamento de Dados
if file_passado and file_presente:
    try:
        def carregar(file):
            return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        df_a = carregar(file_passado)
        df_b = carregar(file_presente)

        # Limpeza preventiva do Ponto de Medição para remover os .000000
        if col_ponto in df_a.columns:
            df_a[col_ponto] = df_a[col_ponto].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        # Seleção e renomeação para o cruzamento
        df_a_clean = df_a[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto'})
        df_b_clean = df_b[[col_placa, col_km]].rename(columns={col_km: 'Atual'})
        
        # Cruzamento (Merge) das planilhas pela Placa
        df_res = pd.merge(df_b_clean, df_a_clean, on=col_placa, how='inner')
        
        # Garantir que as quilometragens sejam números inteiros
        for c in ['Anterior', 'Atual']:
            df_res[c] = pd.to_numeric(df_res[c], errors='coerce').fillna(0).astype(int)
            
        df_res['Diferença (KM)'] = df_res['Atual'] - df_res['Anterior']

        # Exibição de Métricas
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Veículos Comparados", len(df_res))
        m2.metric("Total KM Rodados", f"{df_res['Diferença (KM)'].sum():,.0f} km")
        m3.metric("Maior Rodagem", f"{df_res['Diferença (KM)'].max():,.0f} km")

        # Tabela Detalhada com Cores
        st.markdown("### 📋 Relatório Detalhado")
        
        def color_km(val):
            color = '#ff4b4b' if val < 0 else '#2ecc71'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_res[[col_placa, 'Ponto', 'Anterior', 'Atual', 'Diferença (KM)']].style.map(color_km, subset=['Diferença (KM)']),
            use_container_width=True,
            height=500
        )

        # Botão para baixar resultado
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Relatório Completo", csv, "comparativo_final.csv", "text/csv", use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Erro: Verifique se os nomes das colunas estão corretos! Detalhe: {e}")
else:
    st.info("Por favor, faça o upload das duas planilhas para ver a análise.")
