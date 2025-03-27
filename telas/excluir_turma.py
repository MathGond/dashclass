import sqlite3
import streamlit as st

def obter_turmas():
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("SELECT id, nome, turno, nivel, subnivel FROM turmas")
        return c.fetchall()

def excluir_turma(turma_id):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM controle_aulas WHERE turma_id = ?", (turma_id,))
        c.execute("DELETE FROM turmas WHERE id = ?", (turma_id,))
        conn.commit()

st.subheader("🗑️ Excluir Turma")

turmas = obter_turmas()

if turmas:
    turma = st.selectbox(
        "Selecione a turma para excluir:",
        turmas,
        format_func=lambda x: f"{x[1]} ({x[4]} do {x[3]}, {x[2]})"
    )

    if st.button("Excluir Turma"):
        excluir_turma(turma[0])
        st.success("✅ Turma excluída com sucesso!")
else:
    st.info("📭 Nenhuma turma cadastrada.")
