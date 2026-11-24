from pathlib import Path
import html
import json
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

PASTA_APP = Path(__file__).resolve().parent
ARQUIVO_JSON = PASTA_APP / "dados_turmas.json"
LOGO_ESCOLA = PASTA_APP / "logo_escola.jpg"


# --- Funções de Manipulação do JSON (Com suporte ao Professor e Componente) ---
def carregar_dados():
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                if isinstance(dados, dict) and "turmas" in dados:
                    professor = dados.get("professor", "")
                    componente = dados.get("componente", "Arte")
                    turmas = dados.get("turmas", {})
                else:
                    professor = ""
                    componente = "Arte"
                    turmas = dados  # Compatibilidade com versões anteriores

                # -- Limpeza automática de acentuação antiga nas notas de recuperação
                for turma, alunos in turmas.items():
                    for aluno in alunos:
                        if "recuperação" in aluno:
                            aluno["recuperacao"] = aluno.pop("recuperação")
                return professor, componente, turmas
            except json.JSONDecodeError:
                return "", "Arte", {}
    return "", "Arte", {}


def salvar_dados(professor, componente, turmas):
    dados = {"professor": professor, "componente": componente, "turmas": turmas}
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def gerar_tabela_impressao_html(df):
    linhas_html = []
    for _, row in df.iterrows():
        nome = html.escape(str(row.get("nome_estudante", "")))
        n1 = f"{float(row.get('nota_1', 0.0)):.1f}"
        n2 = f"{float(row.get('nota_2', 0.0)):.1f}"
        n3 = f"{float(row.get('nota_3', 0.0)):.1f}"
        mf = f"{float(row.get('media_final', 0.0)):.1f}"
        rec = f"{float(row.get('recuperacao', 0.0)):.1f}"
        mr = f"{float(row.get('media_recuperada', 0.0)):.1f}"

        linhas_html.append(
            f"<tr>"
            f"<td class='col-nome'>{nome}</td>"
            f"<td class='col-num'>{n1}</td>"
            f"<td class='col-num'>{n2}</td>"
            f"<td class='col-num'>{n3}</td>"
            f"<td class='col-num'>{mf}</td>"
            f"<td class='col-num'>{rec}</td>"
            f"<td class='col-num'>{mr}</td>"
            f"</tr>"
        )

    corpo = "\n".join(linhas_html)
    return f"""
    <div class="tabela-impressao">
        <table>
            <thead>
                <tr>
                    <th class="col-nome">Estudante</th>
                    <th class="col-num">Nota 1</th>
                    <th class="col-num">Nota 2</th>
                    <th class="col-num">Nota 3</th>
                    <th class="col-num">Média Final</th>
                    <th class="col-num">Recuperação</th>
                    <th class="col-num">Média Recuperada</th>
                </tr>
            </thead>
            <tbody>
                {corpo}
            </tbody>
        </table>
    </div>
    """


# 1. Configuração inicial da página
st.set_page_config(
    page_title="Gerenciador de Notas",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializa os dados na sessão carregando do arquivo JSON apenas uma vez
if "dados_carregados" not in st.session_state:
    prof_salvo, comp_salvo, turmas_salvas = carregar_dados()
    st.session_state["professor"] = prof_salvo
    st.session_state["componente"] = comp_salvo
    st.session_state["turmas"] = turmas_salvas
    st.session_state["pagina_atual"] = "Gerenciador"
    st.session_state["turma_ativa"] = None
    st.session_state["dados_carregados"] = True

# --- CSS PERSONALIZADO (Tela, Impressão e Compactação) ---
st.markdown(
    """
    <style>
    /* Deixa os botões da barra lateral mais compactos */
    [data-testid="stSidebar"] button {
        padding: 4px 10px !important;
        min-height: 32px !important;
        font-size: 14px !important;
    }

    /* Compacta o espaçamento vertical entre todos os blocos principais do Streamlit */
    .stApp [data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }

    .anisio {
        font-size: 32px !important;
        margin-bottom: 30px !important;
        padding: 0px !important;
    }
    .expressao {
        font-size: 18px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    [data-testid="stTextInput"], [data-testid="stSelectbox"] {
        margin-bottom: -10px !important;
    }

    /* Na tela normal, oculta a tabela exclusiva de impressão */
    @media screen {
        .tabela-impressao {
            display: none !important;
        }
    }

    @media print {
        @page {
            size: A4 portrait;
            margin: 6mm;
        }
        /* Garante que o bloco oculto do editor não deixe altura vazia */
        [data-testid="stDataEditor"],
        [data-testid="stDataFrame"],
        .stDataEditor,
        .stDataFrame {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* Cola a tabela logo abaixo do cabeçalho/campos */
        .tabela-impressao {
            display: block !important;
            width: 100% !important;
            margin-top: 6px !important;
        }
        
       [data-testid="stSidebar"],
        .stButton,
        .stInfo,
        [data-testid="stDivider"],
        hr,
        label,
        iframe {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        .stMainBlockContainer,
        .block-container,
        [data-testid="stAppViewContainer"] {
            max-width: 100% !important;
            width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        .anisio {
            font-size: 18px !important;
            margin: 0 !important;
            page-break-after: avoid !important;
            break-after: avoid !important;
        }
        .expressao {
            font-size: 12px !important;
            margin: 0 !important;
            page-break-after: avoid !important;
            break-after: avoid !important;
        }

        .tabela-impressao {
            display: block !important;
            width: 100% !important;
            margin-top: 0px !important;
        }

        .tabela-impressao table {
            width: 100% !important;
            border-collapse: collapse !important;
            table-layout: fixed !important;
            font-size: 9px !important;
            font-family: sans-serif !important;
        }

        .tabela-impressao th,
        .tabela-impressao td {
            border: 1px solid #444 !important;
            padding: 2px 3px !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
        }

        .tabela-impressao th {
            background-color: #f0f0f0 !important;
            font-weight: bold !important;
            text-align: center !important;
        }

        .tabela-impressao td.col-nome,
        .tabela-impressao th.col-nome {
            width: 34% !important;
            text-align: left !important;
        }

        .tabela-impressao td.col-num,
        .tabela-impressao th.col-num {
            width: 11% !important;
            text-align: center !important;
        }

        .tabela-impressao tr {
            break-inside: avoid !important;
            page-break-inside: avoid !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- ÁREA CENTRAL: Título Fixo, Professor e Componente Curricular ---
col_logo, col_escola = st.columns([2, 8])

with col_logo:
    st.image(str(LOGO_ESCOLA), width=300)
with col_escola:
    st.markdown(
        """<h2 class="anisio">EMEF Professor Anísio Teixeira</h2>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<h2 class="expressao">Expressão dos resultados</h2>""",
        unsafe_allow_html=True,
    )

col_prof, col_disc = st.columns([1, 1])

with col_prof:
    novo_professor = st.text_input(
        "Docente:",
        value=st.session_state["professor"],
        placeholder="Digite seu nome completo",
    )
    if novo_professor != st.session_state["professor"]:
        st.session_state["professor"] = novo_professor
        salvar_dados(
            st.session_state["professor"],
            st.session_state["componente"],
            st.session_state["turmas"],
        )

with col_disc:
    opcoes_componentes = [
        "Não selecionado",
        "Arte",
        "Ciências",
        "Educação Física",
        "Filosofia",
        "Geografia",
        "História",
        "Língua Espanhola",
        "Língua Inglesa",
        "Língua Portuguesa",
        "Matemática",
    ]

    try:
        indice_atual = opcoes_componentes.index(st.session_state["componente"])
    except ValueError:
        indice_atual = 0

    novo_componente = st.selectbox(
        "Componente Curricular:", opcoes_componentes, index=indice_atual
    )
    if novo_componente != st.session_state["componente"]:
        st.session_state["componente"] = novo_componente
        salvar_dados(
            st.session_state["professor"],
            st.session_state["componente"],
            st.session_state["turmas"],
        )

st.divider()

# --- MENU LATERAL (Sidebar corrigida) ---
if st.sidebar.button("🛠️ Gerenciador de turmas", use_container_width=True):
    st.session_state["pagina_atual"] = "Gerenciador"
    st.session_state["turma_ativa"] = None
    if "selectbox_turmas_lateral" in st.session_state:
        st.session_state["selectbox_turmas_lateral"] = "-- Selecione a turma --"
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("📁 Registro de notas")
turmas_disponíveis = list(st.session_state["turmas"].keys())

if turmas_disponíveis:
    opcoes_turmas = ["-- Selecione a turma --"] + turmas_disponíveis

    indice_selecionado = 0
    if (
        st.session_state["turma_ativa"]
        and st.session_state["turma_ativa"] in turmas_disponíveis
    ):
        indice_selecionado = (
            turmas_disponíveis.index(st.session_state["turma_ativa"]) + 1
        )

    turma_escolhida = st.sidebar.selectbox(
        "Selecione a turma:",
        options=opcoes_turmas,
        index=indice_selecionado,
        key="selectbox_turmas_lateral",
        label_visibility="collapsed",
    )

    if turma_escolhida != "-- Selecione a turma --":
        if st.session_state["turma_ativa"] != turma_escolhida:
            st.session_state["turma_ativa"] = turma_escolhida
            st.session_state["pagina_atual"] = "Gerenciador"
            st.rerun()
else:
    st.sidebar.info("Nenhuma turma cadastrada.")


# --- LÓGICA 1: SEÇÃO GERENCIADOR DE TURMAS (Painel Geral ou Turma Ativa) ---
if st.session_state["pagina_atual"] == "Gerenciador":

    if st.session_state["turma_ativa"]:
        turma_selecionada = st.session_state["turma_ativa"]

        col_botao_calc, col_botao_imprimir = st.columns(2)

        with col_botao_calc:
            botao_calcular = st.button(
                "🧮 Calcular Médias", type="primary", use_container_width=True
            )
        with col_botao_imprimir:
            html_botao_imprimir = """
            <style>
                body {
                    margin: 0;
                    background-color: transparent;
                }
                .btn-streamlit {
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 400;
                    padding: 0.375rem 0.75rem;
                    border-radius: 0.5rem;
                    box-sizing: border-box;
                    width: 100%;
                    height: 38px;
                    background-color: gray;
                    color: rgb(255, 255, 255);
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    text-align: center;
                    text-decoration: none;
                    font-family: "Source Sans Pro", sans-serif;
                    font-size: 14px;
                    cursor: pointer;
                }
                .btn-streamlit:hover {
                    background-color: rgb(255, 51, 51);
                    border-color: rgb(255, 51, 51);
                    color: rgb(255, 255, 255);
                }
            </style>
            <button onclick="parent.window.print()" class="btn-streamlit">
                🖨️ Imprimir / PDF
            </button>
            """
            components.html(html_botao_imprimir, height=45)

        dados_alunos = st.session_state["turmas"][turma_selecionada]
        df_alunos = pd.DataFrame(dados_alunos)

        # Garante que todas as colunas esperadas existam mesmo em dados antigos
        colunas_padrao = {
            "nome_estudante": "",
            "nota_1": 0.0,
            "nota_2": 0.0,
            "nota_3": 0.0,
            "media_final": 0.0,
            "recuperacao": 0.0,
            "media_recuperada": 0.0,
        }
        for col, padrao in colunas_padrao.items():
            if col not in df_alunos.columns:
                df_alunos[col] = padrao

        quantidade_linhas = len(df_alunos)
        altura_dinamica = 35 * quantidade_linhas + 35

        df_editado = st.data_editor(
            df_alunos,
            height=altura_dinamica,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nome_estudante": st.column_config.TextColumn(
                    "Estudante", disabled=True
                ),
                "nota_1": st.column_config.NumberColumn(
                    "Nota 1",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                    format="%.1f",
                ),
                "nota_2": st.column_config.NumberColumn(
                    "Nota 2",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                    format="%.1f",
                ),
                "nota_3": st.column_config.NumberColumn(
                    "Nota 3",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                    format="%.1f",
                ),
                "media_final": st.column_config.NumberColumn(
                    "Média Final", format="%.1f", disabled=True
                ),
                "recuperacao": st.column_config.NumberColumn(
                    "Recuperação",
                    min_value=0.0,
                    max_value=10.0,
                    step=0.1,
                    format="%.1f",
                ),
                "media_recuperada": st.column_config.NumberColumn(
                    "Média Recuperada", format="%.1f", disabled=True
                ),
            },
        )

        # Tabela HTML exclusiva para impressão (oculta na tela, visível no @media print)
        st.markdown(
            gerar_tabela_impressao_html(df_editado),
            unsafe_allow_html=True,
        )

        if botao_calcular:
            lista_atualizada = []
            for _, row in df_editado.iterrows():
                n1 = float(row["nota_1"])
                n2 = float(row["nota_2"])
                n3 = float(row["nota_3"])

                rec = 0.0
                if "recuperacao" in row:
                    rec = float(row["recuperacao"])
                elif "recuperação" in row:
                    rec = float(row["recuperação"])

                med_fin = (n1 + n2 + n3) / 3.0
                med_rec = (med_fin + rec) / 2.0 if rec > 0 else med_fin

                aluno_atualizado = {
                    "nome_estudante": row["nome_estudante"],
                    "nota_1": n1,
                    "nota_2": n2,
                    "nota_3": n3,
                    "media_final": round(med_fin, 2),
                    "recuperacao": rec,
                    "media_recuperada": round(med_rec, 2),
                }
                lista_atualizada.append(aluno_atualizado)

            st.session_state["turmas"][turma_selecionada] = lista_atualizada
            salvar_dados(
                st.session_state["professor"],
                st.session_state["componente"],
                st.session_state["turmas"],
            )
            st.success("Médias recalculadas e alterações salvas com sucesso!")
            st.rerun()

    else:
        st.subheader("🛠️ Painel de Gerenciamento de Turmas")

        aba_criar, aba_editar_existente = st.tabs(
            ["Criar Nova Turma", "Gerenciar Turmas Existentes"]
        )

        with aba_criar:
            st.markdown("#### Cadastrar Nova Turma")
            nome_nova_turma = st.text_input(
                "Nome da Turma (ex: 43):", placeholder="Ex: 43"
            )
            estudantes_texto = st.text_area(
                "Nomes dos Estudantes (digite um nome por linha):",
                placeholder="Adicione a lista em ordem alfabética",
                height=150,
            )

            if st.button("Salvar Nova Turma"):
                if not nome_nova_turma.strip():
                    st.warning("Por favor, insira o nome da turma.")
                elif not estudantes_texto.strip():
                    st.warning("Insira pelo menos um estudante na lista.")
                elif nome_nova_turma in st.session_state["turmas"]:
                    st.error(f"A turma '{nome_nova_turma}' já existe!")
                else:
                    linhas = [
                        l.strip()
                        for l in estudantes_texto.split("\n")
                        if l.strip()
                    ]
                    lista_alunos = []
                    for nome in linhas:
                        lista_alunos.append({
                            "nome_estudante": nome,
                            "nota_1": 0.0,
                            "nota_2": 0.0,
                            "nota_3": 0.0,
                            "media_final": 0.0,
                            "recuperacao": 0.0,
                            "media_recuperada": 0.0,
                        })

                    st.session_state["turmas"][nome_nova_turma] = lista_alunos
                    salvar_dados(
                        st.session_state["professor"],
                        st.session_state["componente"],
                        st.session_state["turmas"],
                    )
                    st.success(f"Turma '{nome_nova_turma}' criada com sucesso!")
                    st.rerun()

        with aba_editar_existente:
            if turmas_disponíveis:
                turma_para_editar = st.selectbox(
                    "Selecione a turma para adicionar/excluir estudantes:",
                    turmas_disponíveis,
                    key="select_editar",
                )

                st.markdown(f"**Estudantes atuais na {turma_para_editar}:**")
                alunos_da_turma = st.session_state["turmas"][turma_para_editar]

                for idx, aluno in enumerate(alunos_da_turma):
                    col_nome, col_btn = st.columns([4, 1])
                    with col_nome:
                        st.text(f"• {aluno['nome_estudante']}")
                    with col_btn:
                        if st.button("Excluir", key=f"del_{turma_para_editar}_{idx}"):
                            alunos_da_turma.pop(idx)
                            st.session_state["turmas"][turma_para_editar] = (
                                alunos_da_turma
                            )
                            salvar_dados(
                                st.session_state["professor"],
                                st.session_state["componente"],
                                st.session_state["turmas"],
                            )
                            st.success("Estudante removido!")
                            st.rerun()

                st.markdown("---")
                st.markdown("##### Adicionar Novo Estudante nesta Turma")
                novo_aluno_nome = st.text_input("Nome do novo estudante:")
                if st.button("Adicionar Estudante"):
                    if novo_aluno_nome.strip():
                        novo_registro = {
                            "nome_estudante": novo_aluno_nome.strip(),
                            "nota_1": 0.0,
                            "nota_2": 0.0,
                            "nota_3": 0.0,
                            "media_final": 0.0,
                            "recuperacao": 0.0,
                            "media_recuperada": 0.0,
                        }
                        st.session_state["turmas"][turma_para_editar].append(
                            novo_registro
                        )
                        salvar_dados(
                            st.session_state["professor"],
                            st.session_state["componente"],
                            st.session_state["turmas"],
                        )
                        st.success(
                            f"Estudante '{novo_aluno_nome}' adicionado com sucesso!"
                        )
                        st.rerun()
                    else:
                        st.warning("Digite o nome do estudante.")
            else:
                st.info("Cadastre uma turma primeiro para poder editá-la.")
