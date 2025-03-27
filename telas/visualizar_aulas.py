import sqlite3
import streamlit as st

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

st.subheader("📚 Visualizar Aulas Registradas")

disciplinas = obter_disciplinas()

if disciplinas:
    disciplina = st.selectbox("Selecione a disciplina:", disciplinas, format_func=lambda x: x[1])
    aulas = obter_aulas_por_disciplina(disciplina[0])
    
    if aulas:
        for num, titulo, conteudo in aulas:
            st.markdown(f"### Aula {num} - {titulo}")
            st.markdown(conteudo)
            st.markdown("---")
    else:
        st.info("📭 Nenhuma aula cadastrada para esta disciplina.")
else:
    st.warning("⚠️ Nenhuma disciplina encontrada.")
