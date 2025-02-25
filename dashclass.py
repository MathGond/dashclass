import os
import pandas as pd
import streamlit as st

# Caminho do arquivo CSV para salvar o progresso
data_file = "registro_aulas.csv"

# Lista atualizada das turmas separadas por turno e disciplinas (agora permitindo múltiplas disciplinas)
matutino_turmas = {
    "3°09": ["FILO"], "2°06": ["HIS", "FILO"], "2°04": ["FILO"], "2°07": ["HIS"], "2°08": ["HIS"], "2°10": ["FILO"],
    "2°05": ["FILO"], "3°10": ["FILO"], "2°02": ["FILO"], "2°01": ["FILO"], "2°03": ["FILO"], "1°06": ["FILO"],
    "1°05": ["FILO"], "3°09": ["FILO"]
}

vespertino_turmas = {
    "1°12 (08)": ["SOCIO"], "2°09": ["HIS"], "1°13 (09)": ["HIS"], "1°11 (07)": ["SOCIO"], "1°05": ["SOCIO"],
    "2°08": ["HIS"], "1°13 (09)": ["SOCIO"], "1°03": ["SOCIO"], "1°04": ["SOCIO"], "1°02": ["SOCIO"], "1°06": ["SOCIO"]
}

# Criar DataFrame inicial se o arquivo não existir
if not os.path.exists(data_file) or "Disciplina" not in pd.read_csv(data_file).columns:
    turmas = []
    disciplinas = []
    turnos = []
    
    for turma, dis_list in matutino_turmas.items():
        for disc in dis_list:
            turmas.append(turma)
            disciplinas.append(disc)
            turnos.append("Matutino")
    
    for turma, dis_list in vespertino_turmas.items():
        for disc in dis_list:
            turmas.append(turma)
            disciplinas.append(disc)
            turnos.append("Vespertino")
    
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

# Dropdown para seleção da turma e disciplina
turma_selecionada = st.selectbox("Selecione a Turma:", turmas_filtradas["Turmas"].unique())

# Filtrar disciplinas disponíveis para a turma selecionada
disciplinas_disponiveis = turmas_filtradas[turmas_filtradas["Turmas"] == turma_selecionada]["Disciplina"].tolist()
disciplina_selecionada = st.selectbox("Selecione a Disciplina:", disciplinas_disponiveis)

# Mostrar disciplina
df_filtro = df[(df["Turmas"] == turma_selecionada) & (df["Disciplina"] == disciplina_selecionada)]
st.write(f"**Disciplina:** {disciplina_selecionada}")

# Criar checkboxes para marcar aulas
aulas_status = []
st.write("### Registro de Aulas")
for i in range(1, 11):
    aula_atual = df_filtro[f"Aula {i}"].values[0]
    status = st.checkbox(f"Aula {i}", value=(aula_atual == "✔️"))
    aulas_status.append("✔️" if status else "❌")

# Botão para salvar
if st.button("Salvar Progresso"):
    for i in range(1, 11):
        df.loc[(df["Turmas"] == turma_selecionada) & (df["Disciplina"] == disciplina_selecionada), f"Aula {i}"] = aulas_status[i-1]
    df.to_csv(data_file, index=False)
    st.success("Progresso salvo com sucesso! ✅")
