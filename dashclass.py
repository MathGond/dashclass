import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, ctx
import os
import dash.exceptions
from dash.dependencies import MATCH, ALL

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

# Criar o aplicativo Dash
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Registro de Aulas", style={'textAlign': 'center'}),
    
    html.Label("Selecione o Turno:"),
    dcc.RadioItems(
        id="turno-radio",
        options=[{"label": "Matutino", "value": "Matutino"}, {"label": "Vespertino", "value": "Vespertino"}],
        value="Matutino",
        inline=True
    ),
    
    html.Label("Selecione a Turma:"),
    dcc.Dropdown(
        id="turma-dropdown",
        clearable=False
    ),
    
    html.Div(id="disciplina-info", style={'marginTop': '10px', 'fontSize': '18px', 'fontWeight': 'bold'}),
    
    html.Div(id="checkboxes-container"),

    html.Button("Salvar Progresso", id="save-button", n_clicks=0, style={'marginTop': '20px'}),
    html.Div(id="save-status", style={'marginTop': '10px'})
])

@app.callback(
    [Output("turma-dropdown", "options"), Output("turma-dropdown", "value")],
    [Input("turno-radio", "value")]
)
def update_turma_options(turno_selecionado):
    turmas_filtradas = df[df["Turno"] == turno_selecionado][["Turmas", "Disciplina"]]
    options = [{"label": f"{row['Turmas']} ({row['Disciplina']})", "value": row['Turmas']} for _, row in turmas_filtradas.iterrows()]
    return options, options[0]["value"]

@app.callback(
    Output("disciplina-info", "children"),
    [Input("turma-dropdown", "value")]
)
def update_disciplina_label(turma_selecionada):
    if not turma_selecionada:
        return ""
    disciplina = df[df["Turmas"] == turma_selecionada]["Disciplina"].values[0]
    return f"Disciplina: {disciplina}"

@app.callback(
    Output("checkboxes-container", "children"),
    [Input("turma-dropdown", "value")]
)
def update_checkboxes(turma_selecionada):
    if not turma_selecionada:
        return ""
    df_filtrado = df[df["Turmas"] == turma_selecionada].iloc[0]
    checkboxes = [
        html.Label([
            dcc.Checklist(
                id={"type": "checkbox", "index": i},
                options=[{"label": f" Aula {i}", "value": "✔️"}],
                value=["✔️"] if df_filtrado[f"Aula {i}"] == "✔️" else []
            )
        ]) for i in range(1, 11)
    ]
    return checkboxes

@app.callback(
    Output("save-status", "children"),
    [Input("save-button", "n_clicks")],
    [State("turma-dropdown", "value")],
    [State({"type": "checkbox", "index": ALL}, "value")]
)
def save_progress(n_clicks, turma_selecionada, checkbox_values):
    if n_clicks == 0 or not turma_selecionada:
        raise dash.exceptions.PreventUpdate  # Evita atualização desnecessária
    
    if not checkbox_values:
        raise dash.exceptions.PreventUpdate  # Evita erro se checkboxes não foram carregados
    
    for i, value in enumerate(checkbox_values, start=1):
        df.loc[df["Turmas"] == turma_selecionada, f"Aula {i}"] = "✔️" if "✔️" in value else "❌"
    df.to_csv(data_file, index=False)
    
    return "Progresso salvo com sucesso! ✅"

# Rodar o Dashboard
if __name__ == "__main__":
    app.run_server(debug=True)
