import sqlite3
import streamlit as st

def adicionar_turma(nome, turno, nivel, subnivel):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO turmas (nome, turno, nivel, subnivel) VALUES (?, ?, ?, ?)",
                  (nome, turno, nivel, subnivel))
        turma_id = c.lastrowid
        # Vincular aulas existentes para mesmo nível e subnível
        c.execute('''
            SELECT a.id FROM aulas a
            JOIN disciplinas d ON a.disciplina_id = d.id
            WHERE d.nivel = ? AND d.subnivel = ?
        ''', (nivel, subnivel))
        aulas = c.fetchall()
        for (aula_id,) in aulas:
            c.execute("INSERT INTO controle_aulas (turma_id, aula_id, status) VALUES (?, ?, '❌')", (turma_id, aula_id))
        conn.commit()

st.subheader("📘 Cadastro de Turmas")

nivel = st.selectbox("Nível de Ensino:", ["Ensino Fundamental", "Ensino Médio", "Ensino Superior", "Curso Técnico / Outro"])
subnivel = ""
if nivel == "Ensino Fundamental":
    subnivel = st.selectbox("Ano:", [f"{i}º ano" for i in range(1, 10)])
elif nivel == "Ensino Médio":
    subnivel = st.selectbox("Ano:", ["1º ano", "2º ano", "3º ano"])

nome_turma = st.text_input("Nome da Turma:")
turno = st.selectbox("Turno:", ["Matutino", "Vespertino", "Noturno"])

if st.button("Cadastrar Turma"):
    if nome_turma and turno and nivel:
        adicionar_turma(nome_turma, turno, nivel, subnivel)
        st.success("✅ Turma cadastrada com sucesso!")
    else:
        st.error("⚠️ Por favor, preencha todos os campos obrigatórios.")
