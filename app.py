import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle Latam Pass", page_icon="✈️", layout="centered")
st.title("💳 Meu Controle Itaucard")
st.markdown("Integrado com Google Sheets")

# --- 1. CONEXÃO COM O GOOGLE SHEETS ---
# O Streamlit busca o link da planilha que você salvou em "Secrets"
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para buscar os dados da planilha em tempo real
def carregar_dados():
    try:
        # ttl=0 garante que ele não use memória antiga e pegue o que está no Sheets agora
        return conn.read(ttl=0)
    except Exception:
        # Se a planilha estiver vazia, cria um modelo básico
        return pd.DataFrame(columns=["data", "estabelecimento", "valor"])

df_existente = carregar_dados()

# --- 2. INTERFACE: FORMULÁRIO DE ENTRADA ---
with st.sidebar:
    st.header("Novo Lançamento")
    with st.form("novo_gasto", clear_on_submit=True):
        loja = st.text_input("Nome do Estabelecimento")
        valor = st.number_input("Valor da Compra (R$)", min_value=0.0, step=0.01)
        enviar = st.form_submit_button("Salvar Gasto")
        
        if enviar:
            if loja and valor > 0:
                # Prepara os novos dados
                nova_linha = pd.DataFrame([{
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "estabelecimento": loja,
                    "valor": valor
                }])
                
                # Junta o novo com o velho
                df_atualizado = pd.concat([df_existente, nova_linha], ignore_index=True)
                
                # Envia tudo de volta para o Google Sheets
                conn.update(data=df_atualizado)
                
                st.success(f"Gasto em {loja} registrado!")
                st.rerun() # Recarrega a página para atualizar a tabela
            else:
                st.warning("Preencha o nome e o valor corretamente.")

# --- 3. EXIBIÇÃO DOS DADOS ---
st.subheader("Histórico de Gastos")

if not df_existente.empty:
    # Exibe a tabela formatada
    st.dataframe(df_existente, use_container_width=True)
    
    # Exibe o total acumulado
    total = df_existente["valor"].sum()
    st.metric("Total Acumulado", f"R$ {total:.2f}")
else:
    st.info("Aguardando o primeiro registro na planilha...")
    st.info("Nenhum gasto registrado ainda.")
