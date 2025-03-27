import sqlite3
import streamlit as st

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
        c.execute("INSERT INTO aulas (disciplina_id, aula_num, titulo, conteudo) VALUES (?, ?, ?, ?)",
                  (disciplina_id, aula_num, titulo, conteudo))
        aula_id = c.lastrowid
        # Vincula essa aula a todas as turmas daquele nível/subnível
        c.execute("SELECT nivel, subnivel FROM disciplinas WHERE id = ?", (disciplina_id,))
        nivel, subnivel = c.fetchone()
        c.execute("SELECT id FROM turmas WHERE nivel = ? AND subnivel = ?", (nivel, subnivel))
        turmas = c.fetchall()
        for turma in turmas:
            c.execute("INSERT INTO controle_aulas (turma_id, aula_id, status) VALUES (?, ?, '❌')", (turma[0], aula_id))
        conn.commit()

st.subheader("🧾 Registro de Aulas")

nivel = st.selectbox("Nível da Disciplina:", ["Ensino Fundamental", "Ensino Médio", "Ensino Superior", "Curso Técnico / Outro"])
subnivel = ""
if nivel == "Ensino Fundamental":
    subnivel = st.selectbox("Ano:", [f"{i}º ano" for i in range(1, 10)])
elif nivel == "Ensino Médio":
    subnivel = st.selectbox("Ano:", ["1º ano", "2º ano", "3º ano"])

disciplina_nome = st.text_input("Nome da Disciplina:")
if st.button("Cadastrar Disciplina") and disciplina_nome:
    adicionar_disciplina(disciplina_nome, nivel, subnivel)
    st.success("✅ Disciplina cadastrada com sucesso!")

disciplinas = obter_disciplinas_por_nivel(nivel, subnivel)
if disciplinas:
    disciplina_selecionada = st.selectbox("Selecione a Disciplina:", disciplinas, format_func=lambda x: x[1])
    aula_num = st.number_input("Número da Aula:", min_value=1, step=1)
    titulo = st.text_input("Título da Aula:")
    conteudo = st.text_area("Conteúdo da Aula:", height=150)
    if st.button("Salvar Aula"):
        salvar_aula(disciplina_selecionada[0], aula_num, titulo, conteudo)
        st.success("📌 Aula salva com sucesso!")
