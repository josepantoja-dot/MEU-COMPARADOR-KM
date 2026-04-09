# 1. Upload dos arquivos
print("Selecione a planilha do DIA PASSADO:")
upload_passado = files.upload()
nome_passado = list(upload_passado.keys())[0]

print("\nSelecione a planilha do DIA PRESENTE:")
upload_presente = files.upload()
nome_presente = list(upload_presente.keys())[0]

# 2. Carregar os dados
df_passado = pd.read_excel(nome_passado) # Use pd.read_csv se for CSV
df_presente = pd.read_excel(nome_presente)

# 3. Defina os nomes das colunas (Ajuste aqui se for diferente na sua planilha)
col_placa = 'Placa'
col_km = 'Quilometragem'
col_ponto = 'Ponto de Medicao'

# 4. Lógica de Comparação
df_a = df_passado[[col_placa, col_ponto, col_km]].rename(columns={col_km: 'KM_Anterior'})
df_b = df_presente[[col_placa, col_km]].rename(columns={col_km: 'KM_Atual'})

# Cruza os dados pela Placa
df_final = pd.merge(df_b, df_a, on=col_placa, how='inner')
df_final['Diferenca_KM'] = df_final['KM_Atual'] - df_final['KM_Anterior']

# Exibir resultado
print("\n--- RESULTADO DA COMPARAÇÃO ---")
display(df_final[[col_placa, col_ponto, 'KM_Anterior', 'KM_Atual', 'Diferenca_KM']])

# 5. Salvar resultado em um novo Excel
df_final.to_excel('resultado_comparacao.xlsx', index=False)
print("\nArquivo 'resultado_comparacao.xlsx' gerado com sucesso!")
