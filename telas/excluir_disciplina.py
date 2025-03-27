import sqlite3
import streamlit as st

def obter_disciplinas():
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome FROM disciplinas")
        return c.fetchall()

def excluir_disciplina(disciplina_id):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        # Excluir registros de controle de aulas relacionadas
        c.execute("DELETE FROM controle_aulas WHERE aula_id IN (SELECT id FROM aulas WHERE disciplina_id = ?)", (disciplina_id,))
        # Excluir aulas associadas
        c.execute("DELETE FROM aulas WHERE disciplina_id = ?", (disciplina_id,))
        # Excluir a disciplina
        c.execute("DELETE FROM disciplinas WHERE id = ?", (disciplina_id,))
        conn.commit()

st.subheader("🗑️ Excluir Disciplina")

disciplinas = obter_disciplinas()

if disciplinas:
    disciplina = st.selectbox("Selecione a disciplina para excluir:", disciplinas, format_func=lambda x: x[1])

    if st.button("Excluir Disciplina"):
        excluir_disciplina(disciplina[0])
        st.success("✅ Disciplina excluída com sucesso!")
else:
    st.info("📭 Nenhuma disciplina cadastrada.")
