import sqlite3
import streamlit as st

def obter_turmas_filtradas(nivel, subnivel, turno):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome FROM turmas WHERE nivel = ? AND subnivel = ? AND turno = ?", (nivel, subnivel, turno))
        return c.fetchall()

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

st.subheader("✅ Controle de Aulas Dadas")

nivel = st.selectbox("Filtrar por Nível:", ["Ensino Fundamental", "Ensino Médio", "Ensino Superior", "Curso Técnico / Outro"])
subnivel = ""
if nivel == "Ensino Fundamental":
    subnivel = st.selectbox("Filtrar por Ano:", [f"{i}º ano" for i in range(1, 10)])
elif nivel == "Ensino Médio":
    subnivel = st.selectbox("Filtrar por Ano:", ["1º ano", "2º ano", "3º ano"])

turno = st.selectbox("Filtrar por Turno:", ["Matutino", "Vespertino", "Noturno"])

turmas_filtradas = obter_turmas_filtradas(nivel, subnivel, turno)
if turmas_filtradas:
    turma_opcao = st.selectbox("Selecione a Turma:", turmas_filtradas, format_func=lambda x: x[1])
    registros = obter_aulas_por_turma(turma_opcao[0])
    if registros:
        for controle_id, disciplina, aula_num, titulo, status in registros:
            marcado = st.checkbox(f"{disciplina} - Aula {aula_num}: {titulo}", value=(status == '✅'), key=f"check_{controle_id}")
            novo_status = '✅' if marcado else '❌'
            if novo_status != status:
                atualizar_status_aula(controle_id, novo_status)
    else:
        st.info("📭 Nenhuma aula registrada para esta turma.")
else:
    st.warning("⚠️ Nenhuma turma encontrada com esse filtro.")
