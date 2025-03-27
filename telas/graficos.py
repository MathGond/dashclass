import sqlite3
import streamlit as st
import plotly.graph_objects as go

def obter_progresso_turmas_filtrado(nivel, subnivel, turno):
    with sqlite3.connect("dashclass.db") as conn:
        c = conn.cursor()
        c.execute('''
            SELECT t.nome,
                   SUM(CASE WHEN ca.status = '✅' THEN 1 ELSE 0 END) AS feitas,
                   COUNT(ca.id) as total
            FROM controle_aulas ca
            JOIN turmas t ON ca.turma_id = t.id
            WHERE t.nivel = ? AND t.subnivel = ? AND t.turno = ?
            GROUP BY ca.turma_id
        ''', (nivel, subnivel, turno))
        return c.fetchall()

st.subheader("📊 Gráfico de Aulas Dadas")

nivel = st.selectbox("Filtrar Nível:", ["Ensino Fundamental", "Ensino Médio", "Ensino Superior", "Curso Técnico / Outro"])
subnivel = ""
if nivel == "Ensino Fundamental":
    subnivel = st.selectbox("Filtrar Ano:", [f"{i}º ano" for i in range(1, 10)])
elif nivel == "Ensino Médio":
    subnivel = st.selectbox("Filtrar Ano:", ["1º ano", "2º ano", "3º ano"])

turno = st.selectbox("Filtrar Turno:", ["Matutino", "Vespertino", "Noturno"])

progresso = obter_progresso_turmas_filtrado(nivel, subnivel, turno)

if progresso:
    nomes = [t[0] for t in progresso]
    feitas = [t[1] for t in progresso]
    totais = [t[2] for t in progresso]
    porcentagens = [(f / t) * 100 if t else 0 for f, t in zip(feitas, totais)]

    fig = go.Figure(data=[
        go.Bar(
            x=nomes,
            y=porcentagens,
            text=[f"{p:.1f}%" for p in porcentagens],
            textposition='auto'
        )
    ])
    fig.update_layout(
        yaxis_title="% de Aulas Dadas",
        xaxis_title="Turmas",
        title="Progresso Geral das Aulas por Turma",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📭 Nenhum dado disponível com esse filtro.")
