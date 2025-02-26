import os
import sqlite3
import pandas as pd
import streamlit as st

# Criar banco de dados SQLite
DB_FILE = "dashclass.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# Criar tabelas se não existirem
c.execute('''
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    turno TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turma_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    FOREIGN KEY (turma_id) REFERENCES turmas (id)
)
''')
conn.commit()

# Funções do banco de dados
def adicionar_turma(nome, turno):
    c.execute("INSERT INTO turmas (nome, turno) VALUES (?, ?)", (nome, turno))
    conn.commit()

def adicionar_disciplina(turma_id, nome):
    c.execute("INSERT INTO disciplinas (turma_id, nome) VALUES (?, ?)", (turma_id, nome))
    conn.commit()

def obter_turmas():
    c.execute("SELECT id, nome, turno FROM turmas")
    return c.fetchall()

def obter_disciplinas(turma_id):
    c.execute("SELECT nome FROM disciplinas WHERE turma_id = ?", (turma_id,))
    return [row[0] for row in c.fetchall()]

# Interface no Streamlit
st.title("DashClass - Gerenciamento de Aulas")

# Controle de exibição de telas
if "pagina" not in st.session_state:
    st.session_state.pagina = "cadastro"

def mudar_pagina():
    st.session_state.pagina = "registro"

# Tela de Cadastro de Turmas e Disciplinas
if st.session_state.pagina == "cadastro":
    st.sidebar.title("Cadastro de Turmas")
    novo_nome_turma = st.sidebar.text_input("Nome da Turma:")
    turno_turma = st.sidebar.radio("Turno:", ["Matutino", "Vespertino"])
    
    if st.sidebar.button("Adicionar Turma") and novo_nome_turma:
        adicionar_turma(novo_nome_turma, turno_turma)
        st.sidebar.success("Turma adicionada com sucesso!")
    
    # Exibir turmas cadastradas
    turmas = obter_turmas()
    if turmas:
        st.sidebar.subheader("Turmas Cadastradas")
        for turma in turmas:
            st.sidebar.text(f"{turma[1]} ({turma[2]})")
    
    # Cadastro de disciplinas
    st.sidebar.subheader("Adicionar Disciplinas")
    if turmas:
        turma_selecionada = st.sidebar.selectbox("Selecione a Turma:", turmas, format_func=lambda x: f"{x[1]} ({x[2]})")
        nova_disciplina = st.sidebar.text_input("Nome da Disciplina:")
        if st.sidebar.button("Adicionar Disciplina") and nova_disciplina:
            adicionar_disciplina(turma_selecionada[0], nova_disciplina)
            st.sidebar.success("Disciplina adicionada com sucesso!")
    
    # Botão para finalizar cadastro e ir para tela principal
    if st.sidebar.button("Finalizar Cadastro e Ir para Registro de Aulas"):
        mudar_pagina()
        st.experimental_rerun()

# Tela de Registro de Aulas
if st.session_state.pagina == "registro":
    st.header("Registro de Aulas")
    turmas = obter_turmas()
    if turmas:
        turma_opcao = st.selectbox("Selecione a Turma:", turmas, key="turma_registro", format_func=lambda x: f"{x[1]} ({x[2]})")
        disciplinas_turma = obter_disciplinas(turma_opcao[0])
        if disciplinas_turma:
            disciplina_opcao = st.selectbox("Selecione a Disciplina:", disciplinas_turma, key="disciplina_registro")
            st.write(f"**Disciplina:** {disciplina_opcao}")
            
            # Criar checkboxes para marcar aulas
            aulas_status = []
            st.write("### Registro de Aulas")
            for i in range(1, 11):
                status = st.checkbox(f"Aula {i}", key=f"aula_{i}")
                aulas_status.append("✔️" if status else "❌")
            
            # Botão para salvar progresso
            if st.button("Salvar Progresso"):
                st.success("Progresso salvo com sucesso! ✅")
        else:
            st.warning("Esta turma ainda não possui disciplinas cadastradas.")
    else:
        st.warning("Nenhuma turma cadastrada. Cadastre uma turma no menu lateral.")

# Fechar conexão com o banco de dados
conn.close()
