import pandas as pd
import streamlit as st
import os

# Caminho do arquivo CSV para salvar o progresso
data_file = "registro_aulas.csv"

# Lista atualizada das turmas separadas por turno e disciplinas
matutino_turmas = {
    "3°09": "FILO", "2°06": "HIS", "2°04": "FILO", "2°07": "HIS", "2°08": "HIS", "2°10": "FILO",
    "2°05": "FILO", "3°10": "FILO", "2°02": "FILO", "2°01": "FILO", "2°03": "FILO", "1°06": "FILO",
    "1°05": "FILO", "3°09": "FILO"
}

vespertino_turmas = {
    "1°12 (08)": "SOCIO", "2°09": "HIS", "1°13 (09)": "HIS", "1°11 (07)": "SOCIO", "1°05": "SOCIO",
    "2°08": "HIS", "1°13 (09)": "SOCIO", "1°03": "SOCIO", "1°04": "SOCIO", "1°02": "SOCIO", "1°06": "SOCIO"
}

# Criar DataFrame inicial se o arquivo não existir
if not os.path.exists(data_file) or "Disciplina" not in pd.read_csv(data_file).columns:
    turmas = list(matutino_turmas.keys()) + list(vespertino_turmas.keys())
    disciplinas = list(matutino_turmas.values()) + list(vespertino_turmas.values())
    turnos = ["Matutino"] * len(matutino_turmas) + ["Vespertino"] * len(vespertino_turmas)
    df = pd.DataFrame({"Turmas": turmas, "Disciplina": disciplinas, "Turno": turnos,
                        **{f"Aula {i}": ["❌"] * len(turmas) for i in range(1, 11)}})
    df.to_csv(data_file, index=False)
else:
    df = pd.read_csv(data_file)

# Garantir que a coluna "Disciplina" está presente no DataFrame
if "Disciplina" not in df.columns:
    df["Disciplina"] = df["Turmas"].map({**matutino_turmas, **vespertino_turmas})
    df.to_csv(data_file, index=False)

# Interface no Streamlit
st.title("Dashboard de Registro de Aulas")

# Seletor de turno
turno_selecionado = st.radio("Selecione o Turno:", ["Matutino", "Vespertino"])

# Filtrar turmas pelo turno selecionado
turmas_filtradas = df[df["Turno"] == turno_selecionado]

# Dropdown para seleção da turma
turma_selecionada = st.selectbox("Selecione a Turma:", turmas_filtradas["Turmas"].tolist())

# Mostrar disciplina
disciplina = df[df["Turmas"] == turma_selecionada]["Disciplina"].values[0]
st.write(f"**Disciplina:** {disciplina}")

# Criar checkboxes para marcar aulas
aulas_status = []
st.write("### Registro de Aulas")
for i in range(1, 11):
    aula_atual = df.loc[df["Turmas"] == turma_selecionada, f"Aula {i}"].values[0]
    status = st.checkbox(f"Aula {i}", value=(aula_atual == "✔️"))
    aulas_status.append("✔️" if status else "❌")

# Botão para salvar
if st.button("Salvar Progresso"):
    for i in range(1, 11):
        df.loc[df["Turmas"] == turma_selecionada, f"Aula {i}"] = aulas_status[i-1]
    df.to_csv(data_file, index=False)
    st.success("Progresso salvo com sucesso! ✅")
