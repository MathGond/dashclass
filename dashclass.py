import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Interface Streamlit
st.set_page_config(page_title="DashClass", layout="centered")
st.markdown("<h2 style='text-align: center;'>DashClass - Gerenciamento de Aulas</h2>", unsafe_allow_html=True)

# Funções com controle de conexão seguro
def adicionar_turma(nome, turno, nivel, subnivel):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO turmas (nome, turno, nivel, subnivel) VALUES (?, ?, ?, ?)", (nome, turno, nivel, subnivel))
        turma_id = c.lastrowid
        c.execute('''
            SELECT a.id FROM aulas a
            JOIN disciplinas d ON a.disciplina_id = d.id
            WHERE d.nivel = ? AND d.subnivel = ?
        ''', (nivel, subnivel))
        aulas_existentes = c.fetchall()
        for (aula_id,) in aulas_existentes:
            c.execute("INSERT INTO controle_aulas (turma_id, aula_id, status) VALUES (?, ?, '❌')", (turma_id, aula_id))
        conn.commit()

def excluir_turma(turma_id):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM controle_aulas WHERE turma_id = ?", (turma_id,))
        c.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
        conn.commit()

def excluir_disciplina(disciplina_id):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM controle_aulas WHERE aula_id IN (SELECT id FROM aulas WHERE disciplina_id = ?)", (disciplina_id,))
        c.execute("DELETE FROM aulas WHERE disciplina_id = ?", (disciplina_id,))
        c.execute("DELETE FROM disciplinas WHERE id = ?", (disciplina_id,))
        conn.commit()

def obter_turmas_filtradas(nivel, subnivel, turno):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome FROM turmas WHERE nivel = ? AND subnivel = ? AND turno = ?", (nivel, subnivel, turno))
        return c.fetchall()

def obter_turmas():
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome, turno, nivel, subnivel FROM turmas")
        return c.fetchall()

def obter_disciplinas():
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome FROM disciplinas")
        return c.fetchall()

def obter_aulas_por_disciplina(disciplina_id):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT aula_num, titulo, conteudo FROM aulas WHERE disciplina_id = ? ORDER BY aula_num", (disciplina_id,))
        return c.fetchall()

def adicionar_disciplina(nome, nivel, subnivel):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO disciplinas (nome, nivel, subnivel) VALUES (?, ?, ?)", (nome, nivel, subnivel))
        conn.commit()

def obter_disciplinas_por_nivel(nivel, subnivel):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome FROM disciplinas WHERE nivel = ? AND subnivel = ?", (nivel, subnivel))
        return c.fetchall()

def salvar_aula(disciplina_id, aula_num, titulo, conteudo):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO aulas (disciplina_id, aula_num, titulo, conteudo) VALUES (?, ?, ?, ?)", (disciplina_id, aula_num, titulo, conteudo))
        aula_id = c.lastrowid
        c.execute("SELECT nivel, subnivel FROM disciplinas WHERE id = ?", (disciplina_id,))
        nivel, subnivel = c.fetchone()
        c.execute("SELECT id FROM turmas WHERE nivel = ? AND subnivel = ?", (nivel, subnivel))
        turmas = c.fetchall()
        for turma in turmas:
            c.execute("INSERT INTO controle_aulas (turma_id, aula_id, status) VALUES (?, ?, '❌')", (turma[0], aula_id))
        conn.commit()

def obter_aulas_por_turma(turma_id):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute('''
            SELECT ca.id, d.nome, a.aula_num, a.titulo, ca.status
            FROM controle_aulas ca
            JOIN aulas a ON ca.aula_id = a.id
            JOIN disciplinas d ON a.disciplina_id = d.id
            WHERE ca.turma_id = ?
            ORDER BY d.nome, a.aula_num
        ''', (turma_id,))
        return c.fetchall()

def atualizar_status_aula(controle_id, status):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE controle_aulas SET status = ? WHERE id = ?", (status, controle_id))
        conn.commit()

def obter_progresso_turmas_filtrado(nivel, subnivel, turno):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute('''
            SELECT t.nome, t.nivel, t.subnivel, t.turno,
                   SUM(CASE WHEN ca.status = '✅' THEN 1 ELSE 0 END) AS feitas,
                   COUNT(ca.id) as total
            FROM controle_aulas ca
            JOIN turmas t ON ca.turma_id = t.id
            WHERE t.nivel = ? AND t.subnivel = ? AND t.turno = ?
            GROUP BY ca.turma_id
        ''', (nivel, subnivel, turno))
        return c.fetchall()

# Nova opção no menu
menu = st.sidebar.radio("Navegação", ["Cadastro de Turmas", "Registro de Aulas", "Controle de Aulas Dadas", "Gráfico de Aulas Dadas", "Visualizar Aulas Registradas", "Excluir Turma", "Excluir Disciplina"])

if menu == "Excluir Disciplina":
    st.header("Excluir Disciplina")
    disciplinas = obter_disciplinas()
    if disciplinas:
        disciplina_opcao = st.selectbox("Selecione a Disciplina para excluir:", disciplinas, format_func=lambda x: x[1])
        if st.button("Excluir Disciplina"):
            excluir_disciplina(disciplina_opcao[0])
            st.success("Disciplina excluída com sucesso!")
