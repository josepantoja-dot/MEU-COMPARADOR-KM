import streamlit as st
import pandas as pd

# 1. Configurações da Página (Ícone e Layout Largo)
st.set_page_config(
    page_title="Frota Inteligente | Comparador KM",
    page_icon="🚛",
    layout="wide"
)

# 2. Estilo CSS Customizado para deixar mais moderno
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Configurações)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830305.png", width=100)
    st.title("Configurações")
    st.info("Ajuste os nomes das colunas conforme seu arquivo.")
    
    # Aqui mudamos os nomes padrão que aparecem nas caixinhas
    col_placa = st.text_input("📝 Nome da Coluna Placa", "Placa")
    col_ponto = st.text_input("📍 Nome da Coluna Ponto", "Ponto de Medição")
    col_km = st.text_input("🔢 Nome da Coluna KM", "Odômetro (KM)")
    
    st.divider()
    st.caption("Versão 2.1 - Nomes Personalizados")

# 4. Cabeçalho Principal
st.title("🚛 Gestão de Frota: Comparativo de Rodagem")
st.subheader("Análise de variação de quilometragem entre períodos")

with st.expander("❓ Como utilizar este sistema?"):
    st.write("""
        1. Prepare duas planilhas (Excel ou CSV).
        2. Garanta que ambas tenham as colunas de **Placa** e **Quilometragem**.
        3. Faça o upload abaixo e veja o resultado instantâneo.
    """)

# 5. Área de Upload em Cards
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 📅 Período Anterior")
    file_passado = st.file_uploader("Arraste o arquivo de ONTEM aqui", type=['csv', 'xlsx'], key="passado")
with c2:
    st.markdown("### 📅 Período Atual")
    file_presente = st.file_uploader("Arraste o arquivo de HOJE aqui", type=['csv', 'xlsx'], key="presente")

# 6. Processamento e Visualização
if file_passado and file_presente:
    try:
        def carregar(file):
            return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        df_a = carregar(file_passado)
        df_b = carregar(file_presente)

        # Cruzamento de dados
        df_a_clean = df_a[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto'})
        df_b_clean = df_b[[col_placa, col_km]].rename(columns={col_km: 'Atual'})
        
        df_res = pd.merge(df_b_clean, df_a_clean, on=col_placa, how='inner')
        df_res['Diferença (KM)'] = df_res['Atual'] - df_res['Anterior']

        # Exibição de Métricas no Topo
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Veículos Analisados", len(df_res))
        m2.metric("Total KM Rodados", f"{df_res['Diferença (KM)'].sum():,.0f} km")
        m3.metric("Média por Veículo", f"{df_res['Diferença (KM)'].mean():,.1f} km")
        m4.metric("Maior Rodagem", f"{df_res['Diferença (KM)'].max():,.0f} km")

       # Tabela Final
        st.markdown("### 📋 Relatório Detalhado")
        
        # Colorir a coluna de diferença (Aqui mudamos de applymap para map)
        def color_km(val):
            color = '#ff4b4b' if val < 0 else '#2ecc71'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_res[[col_placa, 'Ponto', 'Anterior', 'Atual', 'Diferença (KM)']].style.map(color_km, subset=['Diferença (KM)']),
            use_container_width=True,
            height=400
        )

        # Download Centralizado
        st.download_button(
            label="📥 Baixar Relatório Completo",
            data=df_res.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"comparativo_frota_{col_placa}.csv",
            mime="text/csv",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"⚠️ Verifique se as colunas estão corretas! Erro: {e}")
else:
    st.warning("Aguardando o upload das duas planilhas para iniciar a análise.")
