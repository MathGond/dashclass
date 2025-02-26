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

c.execute('''
CREATE TABLE IF NOT EXISTS aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turma_id INTEGER NOT NULL,
    disciplina_id INTEGER NOT NULL,
    aula_num INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT '❌',
    FOREIGN KEY (turma_id) REFERENCES turmas (id),
    FOREIGN KEY (disciplina_id) REFERENCES disciplinas (id)
)
''')
conn.commit()

# Funções do banco de dados
def adicionar_turma(nome, turno):
    c.execute("INSERT INTO turmas (nome, turno) VALUES (?, ?)", (nome, turno))
    conn.commit()

def excluir_turma(turma_id):
    c.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
    c.execute("DELETE FROM disciplinas WHERE turma_id = ?", (turma_id,))
    c.execute("DELETE FROM aulas WHERE turma_id = ?", (turma_id,))
    conn.commit()

def adicionar_disciplina(turma_id, nome):
    c.execute("INSERT INTO disciplinas (turma_id, nome) VALUES (?, ?)", (turma_id, nome))
    conn.commit()
    disciplina_id = c.lastrowid
    for aula_num in range(1, 11):
        c.execute("INSERT INTO aulas (turma_id, disciplina_id, aula_num) VALUES (?, ?, ?)", (turma_id, disciplina_id, aula_num))
    conn.commit()

def obter_turmas():
    c.execute("SELECT id, nome, turno FROM turmas")
    return c.fetchall()

def obter_disciplinas(turma_id):
    c.execute("SELECT id, nome FROM disciplinas WHERE turma_id = ?", (turma_id,))
    return c.fetchall()

def obter_status_aulas(turma_id, disciplina_id):
    c.execute("SELECT aula_num, status FROM aulas WHERE turma_id = ? AND disciplina_id = ? ORDER BY aula_num", (turma_id, disciplina_id))
    return dict(c.fetchall())

def atualizar_status_aula(turma_id, disciplina_id, aula_num, status):
    c.execute("UPDATE aulas SET status = ? WHERE turma_id = ? AND disciplina_id = ? AND aula_num = ?", (status, turma_id, disciplina_id, aula_num))
    conn.commit()

# Interface no Streamlit
st.markdown("<h2 style='text-align: center;'>DashClass - Gerenciamento de Aulas</h2>", unsafe_allow_html=True)


# Controle de exibição de telas
if "pagina" not in st.session_state:
    st.session_state.pagina = "cadastro"

def mudar_pagina(pagina):
    st.session_state.pagina = pagina
    st.rerun()

# Menu de navegação
menu = st.sidebar.radio("Navegação", ["Cadastro de Turmas", "Registro de Aulas"])

if menu == "Cadastro de Turmas":
    st.sidebar.title("Cadastro de Turmas")
    novo_nome_turma = st.sidebar.text_input("Nome da Turma:")
    turno_turma = st.sidebar.radio("Turno:", ["Matutino", "Vespertino"])
    
    if st.sidebar.button("Adicionar Turma") and novo_nome_turma:
        adicionar_turma(novo_nome_turma, turno_turma)
        st.sidebar.success("Turma adicionada com sucesso!")
    
    turmas = obter_turmas()
    if turmas:
        st.sidebar.subheader("Gerenciar Turmas")
        for turma in turmas:
            col1, col2 = st.sidebar.columns([3, 1])
            col1.text(f"{turma[1]} ({turma[2]})")
            if col2.button("❌", key=f"del_turma_{turma[0]}"):
                excluir_turma(turma[0])
                st.sidebar.warning("Turma excluída!")
                st.rerun()
    
    st.sidebar.subheader("Adicionar Disciplinas")
    if turmas:
        turma_selecionada = st.sidebar.selectbox("Selecione a Turma:", turmas, format_func=lambda x: f"{x[1]} ({x[2]})")
        nova_disciplina = st.sidebar.text_input("Nome da Disciplina:")
        if st.sidebar.button("Adicionar Disciplina") and nova_disciplina:
            adicionar_disciplina(turma_selecionada[0], nova_disciplina)
            st.sidebar.success("Disciplina adicionada com sucesso!")

elif menu == "Registro de Aulas":
    st.header("Registro de Aulas")
    turmas = obter_turmas()
    if turmas:
        turma_opcao = st.selectbox("Selecione a Turma:", turmas, key="turma_registro", format_func=lambda x: f"{x[1]} ({x[2]})")
        disciplinas_turma = obter_disciplinas(turma_opcao[0])
        if disciplinas_turma:
            disciplina_opcao = st.selectbox("Selecione a Disciplina:", disciplinas_turma, key="disciplina_registro")
            st.write(f"**Disciplina:** {disciplina_opcao[1]}")
            
            status_aulas = obter_status_aulas(turma_opcao[0], disciplina_opcao[0])
            
            st.write("### Registro de Aulas")
            for i in range(1, 11):
                status = status_aulas.get(i, "❌")
                checked = status == "✔️"
                if st.checkbox(f"Aula {i}", value=checked, key=f"aula_{turma_opcao[0]}_{disciplina_opcao[0]}_{i}"):
                    atualizar_status_aula(turma_opcao[0], disciplina_opcao[0], i, "✔️")
                else:
                    atualizar_status_aula(turma_opcao[0], disciplina_opcao[0], i, "❌")
            
            st.success("Progresso salvo automaticamente! ✅")
        else:
            st.warning("Esta turma ainda não possui disciplinas cadastradas.")
    else:
        st.warning("Nenhuma turma cadastrada. Cadastre uma turma no menu lateral.")

# Fechar conexão com o banco de dados
conn.close()
