import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. FUNÇÃO PARA CRIAR O BANCO DE DADOS (Onde os gastos ficam salvos)
def init_db():
    conn = sqlite3.connect('meus_gastos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS compras 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  data TEXT, estabelecimento TEXT, valor REAL)''')
    conn.commit()
    conn.close()

# 2. FUNÇÃO PARA SALVAR UM NOVO GASTO
def salvar_dados(loja, valor):
    conn = sqlite3.connect('meus_gastos.db')
    c = conn.cursor()
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO compras (data, estabelecimento, valor) VALUES (?, ?, ?)",
              (data_atual, loja, valor))
    conn.commit()
    conn.close()

# --- INTERFACE DO APP (O que aparece na tela) ---
st.set_page_config(page_title="Controle Latam Pass", page_icon="✈️")
st.title("💳 Meu Controle Itaucard")

init_db()

# Formulário para inserir gasto manualmente (enquanto não automatizamos)
with st.form("novo_gasto"):
    st.write("Adicionar Gasto Manual")
    loja = st.text_input("Nome do Estabelecimento")
    valor = st.number_input("Valor da Compra (R$)", min_value=0.0, step=0.01)
    enviar = st.form_submit_button("Salvar Gasto")
    
    if enviar and loja:
        salvar_dados(loja, valor)
        st.success(f"Gasto em {loja} salvo com sucesso!")

# Mostrar a tabela de gastos
st.divider()
st.subheader("Histórico de Gastos")
conn = sqlite3.connect('meus_gastos.db')
df = pd.read_sql_query("SELECT data, estabelecimento, valor FROM compras ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True)
    st.metric("Total Gasto", f"R$ {df['valor'].sum():.2f}")
else:
    st.info("Nenhum gasto registrado ainda.")