import streamlit as st
import pandas as pd

# 1. Configurações da Página
st.set_page_config(
    page_title="Frota Inteligente | Comparador KM",
    page_icon="🚛",
    layout="wide"
)

# 2. CSS Blindado para Modo Escuro Fixo e Texto Legível
st.markdown("""
    <style>
    /* Força o fundo escuro no corpo do app */
    .stApp {
        background-color: #0e1117 !important;
    }
    
    /* Estilização dos cards de métricas */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        padding: 20px !important;
        border-radius: 12px !important;
    }
    
    /* Cores das métricas */
    div[data-testid="stMetricValue"] > div { color: #38bdf8 !important; }
    div[data-testid="stMetricLabel"] > label { color: #94a3b8 !important; }

    /* Caixas de upload */
    .stFileUploader {
        background-color: #1e293b !important;
        border: 2px dashed #38bdf8 !important;
        border-radius: 12px !important;
    }

    /* Forçar cores de títulos e textos gerais para branco/claro */
    h1, h2, h3, p, span, label {
        color: #fafafa !important;
    }

    /* Ajuste para a tabela (DataFrame) */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar (Lateral)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830305.png", width=100)
    st.title("Configurações")
    col_placa = st.text_input("📝 Nome da Coluna Placa", "Placa")
    col_ponto = st.text_input("📍 Nome da Coluna Ponto", "Ponto de Medição")
    col_km = st.text_input("🔢 Nome da Coluna KM", "Odômetro (KM)")
    st.divider()
    st.caption("Versão 6.0 - Final Fix (Cores & Visibilidade)")

# 4. Cabeçalho
st.title("🚛 Dashboard: Comparativo de Rodagem")
st.write("Análise automática e visual de variação de quilometragem entre períodos.")

# 5. Área de Upload
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 🕒 Planilha ANTERIOR")
    file_passado = st.file_uploader("Arquivo de ONTEM", type=['csv', 'xlsx'], key="passado")
with c2:
    st.markdown("### 🕒 Planilha ATUAL")
    file_presente = st.file_uploader("Arquivo de HOJE", type=['csv', 'xlsx'], key="presente")

# 6. Processamento de Dados
if file_passado and file_presente:
    try:
        def carregar(file):
            return pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
        
        df_a = carregar(file_passado)
        df_b = carregar(file_presente)

        # Limpeza do Ponto de Medição (remove .0)
        if col_ponto in df_a.columns:
            df_a[col_ponto] = df_a[col_ponto].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

        # Preparação dos DataFrames para o cruzamento
        df_a_clean = df_a[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'Anterior', col_ponto: 'Ponto', col_placa: 'Placa'})
        df_b_clean = df_b[[col_placa, col_km]].rename(columns={col_km: 'Atual', col_placa: 'Placa'})
        
        # Cruzamento (Merge)
        df_res = pd.merge(df_b_clean, df_a_clean, on='Placa', how='inner')
        
        # Conversão para números inteiros
        for c in ['Anterior', 'Atual']:
            df_res[c] = pd.to_numeric(df_res[c], errors='coerce').fillna(0).astype(int)
            
        df_res['Diferença (KM)'] = df_res['Atual'] - df_res['Anterior']

        # 7. Cards de Métricas
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Veículos", len(df_res))
        m2.metric("Total KM", f"{df_res['Diferença (KM)'].sum():,.0f}")
        m3.metric("Média", f"{df_res['Diferença (KM)'].mean():.1f}")
        m4.metric("Máximo", f"{df_res['Diferença (KM)'].max()}")

        # 8. Tabela Detalhada com Estilo Zebra Colorido e Texto Visível
        st.markdown("### 📋 Relatório Detalhado")
        
        # Paleta de cores de fundo suaves (pastéis)
        lista_cores = ['#ffffff', '#f0f9ff', '#f0fdf4', '#fff7ed']

        # Função que aplica a cor de fundo E garante que o texto seja escuro
        def aplicar_estilo_linha(row):
            cor_fundo = lista_cores[int(row.name) % len(lista_cores)]
            # color: #1e293b força o texto a ser azul escuro para aparecer sobre o fundo claro
            return [f'background-color: {cor_fundo}; color: #1e293b; font-weight: 500'] * len(row)

        def style_texto_km(val):
            # Cor para a Diferença: Vermelho para erro, Verde para aumento
            color = '#e11d48' if val < 0 else '#16a34a' 
            return f'color: {color}; font-weight: bold; font-size: 16px'

        # Aplicando a estilização
        df_colorido = df_res[['Placa', 'Ponto', 'Anterior', 'Atual', 'Diferença (KM)']].style \
            .apply(aplicar_estilo_linha, axis=1) \
            .map(style_texto_km, subset=['Diferença (KM)'])

        # Exibindo a tabela final
        st.dataframe(df_colorido, use_container_width=True, height=550)
        
        # Botão de Download
        csv = df_res.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 BAIXAR RELATÓRIO COMPLETO", csv, "relatorio_frota_pro.csv", "text/csv", use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Ocorreu um erro no processamento: {e}")
else:
    st.info("Aguardando o upload das duas planilhas para iniciar a análise.")
