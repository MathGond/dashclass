import streamlit as st
from pathlib import Path

# Configuração da interface
st.set_page_config(page_title="DashClass", layout="centered")
st.markdown("<h2 style='text-align: center;'>DashClass - Gerenciamento de Aulas</h2>", unsafe_allow_html=True)

# Menu lateral
st.sidebar.markdown("### Navegação")
menu_opcoes = [
    "Cadastro de Turmas",
    "Registro de Aulas",
    "Controle de Aulas Dadas",
    "Gráfico de Aulas Dadas",
    "Visualizar Aulas Registradas",
    "Excluir Turma",
    "Excluir Disciplina"
]
menu = st.sidebar.radio("Selecione a opção desejada:", menu_opcoes)

# Caminho base para as telas
tela_path = Path("telas")

# Mapeamento das telas para seus respectivos arquivos .py
telas = {
    "Cadastro de Turmas": "cadastro_turmas.py",
    "Registro de Aulas": "registro_aulas.py",
    "Controle de Aulas Dadas": "controle_aulas.py",
    "Gráfico de Aulas Dadas": "graficos.py",
    "Visualizar Aulas Registradas": "visualizar_aulas.py",
    "Excluir Turma": "excluir_turma.py",
    "Excluir Disciplina": "excluir_disciplina.py"
}

# Execução da tela selecionada
tela_arquivo = tela_path / telas[menu]

if tela_arquivo.exists():
    with open(tela_arquivo, "r", encoding="utf-8") as f:
        exec(f.read())
else:
    st.error("Tela não encontrada. Verifique se o arquivo existe em /telas.")
