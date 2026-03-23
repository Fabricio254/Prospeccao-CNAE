import streamlit as st
import requests
import pandas as pd
import time
import re
import io

st.set_page_config(
    page_title="Locvix — Prospecção de Clientes",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {font-size:2.2rem; font-weight:700; color:#e67e22; margin-bottom:0.2rem;}
    .sub-title  {font-size:1rem; color:#555; margin-bottom:1.5rem;}
    .tag-seg    {background:#fff3e0; border-left:4px solid #e67e22; padding:8px 14px;
                 border-radius:4px; font-size:.9rem; margin-bottom:.8rem;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GRUPOS DE CNAE — clientes que CONTRATAM guindastes e maquinário pesado
# ══════════════════════════════════════════════════════════════════════════════
GRUPOS_CNAE = {

    "🏗️ Construção Civil e Obras": {
        "desc": "Maior mercado: içamento de vigas, lajes, estruturas pré-fabricadas e montagem metálica.",
        "cnaes": {
            "4120400": "Construção de edifícios",
            "4211101": "Construção de rodovias e ferrovias",
            "4221901": "Construção de barragens e represas",
            "4222701": "Construção de redes de abastecimento de água",
            "4223500": "Construção de redes de transportes por dutos",
            "4291000": "Obras portuárias, marítimas e fluviais",
            "4292801": "Montagem de estruturas metálicas",
            "4311801": "Demolição de edifícios e outras estruturas",
            "4312600": "Perfurações e sondagens",
            "4321500": "Instalação e manutenção elétrica",
            "4322301": "Instalações hidráulicas, sanitárias e de gás",
            "4330401": "Impermeabilização em obras de engenharia civil",
            "4391600": "Obras de fundações",
            "4399101": "Administração de obras",
            "4399103": "Obras de terraplanagem",
            "4110700": "Incorporação de empreendimentos imobiliários",
        }
    },

    "🏭 Indústria — Manutenção e Instalação": {
        "desc": "Paradas programadas, instalação/remoção de máquinas pesadas e manutenção industrial.",
        "cnaes": {
            "3321000": "Instalação de máquinas e equipamentos industriais",
            "3311200": "Manutenção de tanques e reservatórios metálicos",
            "3312102": "Manutenção e reparação de equipamentos para a indústria",
            "3313901": "Manutenção de geradores, transformadores e motores",
            "3314701": "Manutenção de máquinas motrizes não elétricas",
            "3314799": "Manutenção e reparação de outras máquinas e equipamentos",
            "2411300": "Produção de ferro-gusa",
            "2531401": "Produção de forjados de aço",
            "2710401": "Fabricação de geradores de corrente contínua e alternada",
            "2812700": "Fabricação de equipamentos hidráulicos e pneumáticos",
            "2861500": "Fabricação de ferramentas",
            "2941700": "Fabricação de peças para sistema motor de veículos",
            "3011302": "Construção de embarcações para transporte",
            "2330301": "Fabricação de estruturas pré-moldadas de concreto",
            "1710900": "Fabricação de celulose e outras pastas",
            "1921700": "Fabricação de produtos do refino de petróleo",
        }
    },

    "⚡ Energia — Eólica, Elétrica, Óleo e Gás": {
        "desc": "Montagem de torres eólicas, instalação de transformadores e manutenção em refinarias.",
        "cnaes": {
            "3511501": "Geração de energia elétrica",
            "3511502": "Geração de energia elétrica de origem eólica",
            "3511503": "Geração de energia elétrica solar fotovoltaica",
            "3512300": "Transmissão de energia elétrica",
            "3514000": "Distribuição de energia elétrica",
            "0600001": "Extração de petróleo e gás natural",
            "0910600": "Atividades de apoio à extração de petróleo e gás",
            "4321500": "Instalação e manutenção elétrica",
            "3530000": "Produção e distribuição de vapor e ar condicionado",
            "4322302": "Instalação e manutenção de sistemas de ar condicionado",
            "3600601": "Captação, tratamento e distribuição de água",
        }
    },

    "⛏️ Mineração e Siderurgia": {
        "desc": "Movimentação contínua de equipamentos pesados em minas, usinas e fundições.",
        "cnaes": {
            "0710301": "Extração de minério de ferro",
            "0721901": "Extração de minério de alumínio",
            "0722701": "Extração de minério de estanho",
            "0723501": "Extração de minério de manganês",
            "0724301": "Extração de minério de metais preciosos",
            "0729401": "Extração de minerais metálicos não-ferrosos",
            "0810001": "Extração de ardósia e beneficiamento",
            "0891600": "Extração de minerais para fabricação de adubos",
            "2411300": "Produção de ferro-gusa",
            "2412100": "Produção de ferroligas",
            "2421100": "Produção de semiacabados de aço",
            "2422901": "Produção de laminados planos de aço",
            "2423701": "Produção de tubos de aço sem costura",
        }
    },

    "🚛 Transporte Pesado e Logística": {
        "desc": "Carga/descarga de cargas superdimensionadas, movimentação de contêineres e máquinas.",
        "cnaes": {
            "4930201": "Transporte rodoviário de carga — exceto produtos perigosos",
            "4930202": "Transporte rodoviário de carga — produtos perigosos",
            "5011401": "Transporte marítimo de cabotagem",
            "5012201": "Transporte marítimo de longo curso — carga",
            "5091201": "Transporte por navegação de travessia — carga",
            "5111100": "Transporte aéreo de passageiros regular",
            "5120000": "Transporte aéreo de carga",
            "5211701": "Armazéns gerais — emissão de warrant",
            "5212500": "Carga e descarga",
            "5231101": "Administração de portos e terminais",
            "5250801": "Agenciamento de cargas",
        }
    },

    "🌾 Agronegócio — Silos e Maquinário": {
        "desc": "Instalação de silos, movimentação de colheitadeiras e manutenção de irrigação.",
        "cnaes": {
            "0161001": "Atividade de apoio à agricultura — colheita",
            "0163600": "Atividade de pós-colheita",
            "0111301": "Cultivo de trigo",
            "0115600": "Cultivo de soja",
            "0141501": "Criação de bovinos para corte",
            "0155501": "Criação de frango de corte",
            "2833000": "Fabricação de máquinas e equipamentos para agricultura",
            "4612500": "Representantes comerciais de insumos agropecuários",
            "1011201": "Frigorífico — abate de bovinos",
            "1012101": "Abate de suínos, aves e outros pequenos animais",
        }
    },

    "🎪 Eventos, Palcos e Estruturas Temporárias": {
        "desc": "Montagem de palcos, estruturas metálicas e equipamentos em grandes eventos.",
        "cnaes": {
            "8230001": "Organização de feiras, congressos, exposições e festas",
            "9001906": "Atividades de sonorização e de iluminação",
            "4292801": "Montagem de estruturas metálicas",
            "9321200": "Parques de diversão e parques temáticos",
            "9001901": "Produção teatral",
            "9001902": "Produção musical",
            "9001905": "Produção de rodeios, vaquejadas e similares",
            "5911101": "Estúdios cinematográficos",
        }
    },

    "🏢 Portos e Terminais — Espírito Santo": {
        "desc": "Portos de Vitória, Tubarão e Praia Mole — alta demanda por guindastes na região ES.",
        "cnaes": {
            "5231101": "Administração de portos e terminais",
            "5231102": "Operações de terminais",
            "5231103": "Gestão de terminais aquaviários",
            "5232000": "Atividades de agenciamento marítimo",
            "5239701": "Serviços de praticagem",
            "4291000": "Obras portuárias, marítimas e fluviais",
            "5212500": "Carga e descarga",
            "0600001": "Extração de petróleo e gás natural",
            "0910600": "Atividades de apoio à extração de petróleo e gás",
        }
    },
}

# ── Dicionário plano com todos os CNAEs dos grupos ───────────────────────────
TODOS_CNAES: dict = {}
for _g in GRUPOS_CNAE.values():
    TODOS_CNAES.update(_g["cnaes"])

ESTADOS = ["", "AC","AL","AP","AM","BA","CE","DF","ES","GO",
           "MA","MT","MS","MG","PA","PB","PR","PE","PI",
           "RJ","RN","RS","RO","RR","SC","SP","SE","TO"]


# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE API
# ══════════════════════════════════════════════════════════════════════════════

def buscar_por_cnae(cnae: str, municipio: str, estado: str, pagina: int = 1):
    url = "https://api.casadosdados.com.br/v2/public/cnpj/pesquisa"
    payload = {
        "query": {"cnae_fiscal_principal": {"codigo": cnae}, "situacao_cadastral": "ATIVA"},
        "range_query": {},
        "extras": {
            "somente_mei": False, "excluir_mei": False,
            "com_contato_telefonico": False, "com_email": False,
            "incluir_atividade_secundaria": False, "com_natureza_juridica": []
        },
        "page": pagina
    }
    if municipio.strip():
        payload["query"]["municipio"] = municipio.strip().upper()
    if estado.strip():
        payload["query"]["uf"] = estado.strip().upper()
    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json().get("data", {}).get("cnpj", [])
    except Exception:
        pass
    return []


def buscar_cnpj(cnpj: str):
    limpo = re.sub(r"\D", "", cnpj)
    for url in [
        f"https://brasilapi.com.br/api/cnpj/v1/{limpo}",
        f"https://www.cnpj.ws/cnpj/{limpo}",
        f"https://receitaws.com.br/v1/cnpj/{limpo}",
    ]:
        try:
            r = requests.get(url, timeout=12)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(0.3)
    return None


def formatar(emp: dict) -> dict:
    tel  = (emp.get("ddd_telefone_1") or "") + (emp.get("telefone_1") or "")
    tel2 = (emp.get("ddd_telefone_2") or "") + (emp.get("telefone_2") or "")
    cap  = emp.get("capital_social") or 0
    try:    cap_fmt = f"R$ {float(cap):,.2f}"
    except: cap_fmt = str(cap)
    return {
        "CNPJ":              emp.get("cnpj", ""),
        "Razão Social":      emp.get("razao_social", ""),
        "Nome Fantasia":     emp.get("nome_fantasia", ""),
        "Situação":          emp.get("situacao_cadastral", ""),
        "Telefone 1":        tel,
        "Telefone 2":        tel2,
        "Email":             emp.get("email", ""),
        "Município":         emp.get("municipio", ""),
        "UF":                emp.get("uf", ""),
        "Logradouro":        f"{emp.get('logradouro','')} {emp.get('numero','')} {emp.get('complemento','')}".strip(),
        "Bairro":            emp.get("bairro", ""),
        "CEP":               emp.get("cep", ""),
        "Porte":             emp.get("porte", ""),
        "Natureza Jurídica": emp.get("natureza_juridica", ""),
        "Capital Social":    cap_fmt,
        "Data de Abertura":  emp.get("data_inicio_atividade", ""),
        "CNAE Principal":    str(emp.get("cnae_fiscal", "")),
        "Descrição CNAE":    emp.get("cnae_fiscal_descricao", ""),
    }


# ══════════════════════════════════════════════════════════════════════════════
# INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<p class="main-title">🏗️ Locvix — Prospecção de Clientes</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Encontre empresas que podem contratar locação de guindastes e maquinário pesado</p>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filtros de Busca")
    aba = st.radio("Modo:", ["🔍 Buscar por Segmento / CNAE", "🏢 Consultar CNPJ"])

    if aba == "🔍 Buscar por Segmento / CNAE":

        modo = st.radio(
            "Selecionar CNAE por:",
            ["🎯 Segmento (recomendado)", "✏️ Código Manual"]
        )

        if modo == "🎯 Segmento (recomendado)":
            segmento = st.selectbox("Segmento:", list(GRUPOS_CNAE.keys()))
            cnaes_seg = GRUPOS_CNAE[segmento]["cnaes"]
            st.markdown(
                f'<div class="tag-seg">📌 {GRUPOS_CNAE[segmento]["desc"]}</div>',
                unsafe_allow_html=True
            )
            cnae_final = st.selectbox(
                "CNAE:",
                list(cnaes_seg.keys()),
                format_func=lambda x: f"{x} — {cnaes_seg[x]}"
            )
        else:
            cnae_final = st.text_input("Código CNAE:", placeholder="Ex: 4292801").strip()
            if not cnae_final:
                st.warning("Digite um código CNAE.")
                cnae_final = ""

        st.divider()
        municipio = st.text_input("Município:", placeholder="Ex: SERRA")
        idx_es    = ESTADOS.index("ES")
        estado    = st.selectbox("Estado:", ESTADOS, index=idx_es)
        paginas   = st.slider("Páginas de resultado:", 1, 10, 3,
                              help="Cada página = até 20 empresas")
        st.divider()
        btn_buscar = st.button("🔍 Buscar Empresas", type="primary", use_container_width=True)

    else:
        cnpj_input = st.text_input("CNPJ:", placeholder="00.000.000/0001-00")
        btn_cnpj   = st.button("🔍 Consultar", type="primary", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTADO — BUSCA POR CNAE
# ══════════════════════════════════════════════════════════════════════════════
if aba == "🔍 Buscar por Segmento / CNAE" and btn_buscar:

    if not cnae_final:
        st.error("Selecione ou informe um CNAE antes de buscar.")
        st.stop()

    desc = TODOS_CNAES.get(cnae_final, cnae_final)
    st.info(f"**CNAE {cnae_final}** — {desc}")

    todas = []
    barra = st.progress(0, text="Iniciando busca…")
    for i, pg in enumerate(range(1, paginas + 1), 1):
        barra.progress(i / paginas, text=f"Buscando página {pg} de {paginas}…")
        todas.extend(buscar_por_cnae(cnae_final, municipio, estado, pg))
        if pg < paginas:
            time.sleep(0.8)
    barra.empty()

    if not todas:
        st.error("Nenhuma empresa encontrada. Tente outro CNAE, município ou estado.")
        st.stop()

    df = pd.DataFrame([formatar(e) for e in todas])

    # ── Métricas ──────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total encontrado",  len(df))
    c2.metric("Com telefone",      int((df["Telefone 1"] != "").sum()))
    c3.metric("Com e-mail",        int((df["Email"]      != "").sum()))
    c4.metric("Ativas",            int((df["Situação"]   == "ATIVA").sum()))

    st.divider()

    # ── Filtros rápidos ───────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    apenas_ativas = col1.checkbox("Apenas ativas",       value=True)
    apenas_tel    = col2.checkbox("Apenas com telefone", value=False)
    apenas_email  = col3.checkbox("Apenas com e-mail",   value=False)

    df_vis = df.copy()
    if apenas_ativas: df_vis = df_vis[df_vis["Situação"] == "ATIVA"]
    if apenas_tel:    df_vis = df_vis[df_vis["Telefone 1"] != ""]
    if apenas_email:  df_vis = df_vis[df_vis["Email"] != ""]

    st.markdown(f"**{len(df_vis)} empresas exibidas**")

    # ── Tabela ────────────────────────────────────────────────────────────────
    st.dataframe(
        df_vis,
        use_container_width=True,
        height=520,
        column_config={
            "CNPJ":          st.column_config.TextColumn("CNPJ",          width="medium"),
            "Razão Social":  st.column_config.TextColumn("Razão Social",  width="large"),
            "Nome Fantasia": st.column_config.TextColumn("Nome Fantasia", width="large"),
            "Telefone 1":    st.column_config.TextColumn("Telefone",      width="small"),
            "Email":         st.column_config.TextColumn("E-mail",        width="medium"),
            "Município":     st.column_config.TextColumn("Município",     width="medium"),
            "UF":            st.column_config.TextColumn("UF",            width="small"),
            "Porte":         st.column_config.TextColumn("Porte",         width="small"),
        }
    )

    # ── Detalhe individual ────────────────────────────────────────────────────
    st.divider()
    st.subheader("🔎 Ver dados completos de uma empresa")
    lista_cnpjs = df_vis["CNPJ"].dropna().unique().tolist()
    cnpj_sel = st.selectbox("Selecione o CNPJ:", [""] + lista_cnpjs)

    if cnpj_sel:
        with st.spinner("Consultando dados completos…"):
            det = buscar_cnpj(cnpj_sel)
        if det:
            emp = formatar(det)
            col1, col2, col3 = st.columns(3)
            col1.metric("Razão Social",   emp["Razão Social"])
            col1.metric("Nome Fantasia",  emp["Nome Fantasia"] or "—")
            col1.metric("Situação",       emp["Situação"])
            col2.metric("Telefone 1",     emp["Telefone 1"] or "—")
            col2.metric("Telefone 2",     emp["Telefone 2"] or "—")
            col2.metric("E-mail",         emp["Email"] or "—")
            col3.metric("Município / UF", f"{emp['Município']} / {emp['UF']}")
            col3.metric("Porte",          emp["Porte"] or "—")
            col3.metric("Capital Social", emp["Capital Social"])

            with st.expander("📋 Todos os campos"):
                for k, v in emp.items():
                    if v:
                        st.write(f"**{k}:** {v}")

            with st.expander("💡 Sugestão de abordagem comercial"):
                st.markdown(f"""
A **{emp['Razão Social']}** é uma empresa do setor **{desc}**, localizada em
**{emp['Município']} / {emp['UF']}**.

**Como abordar:**
- Apresente a Locvix como especialista em locação de guindastes e maquinário pesado na região ES
- Destaque disponibilidade imediata, frota variada e suporte técnico
- Pergunte sobre próximas obras / paradas programadas / projetos de expansão
- Ofereça visita técnica sem compromisso

**Contato sugerido:**
📞 {emp['Telefone 1'] or emp['Telefone 2'] or '(sem telefone cadastrado)'}
📧 {emp['Email'] or '(sem e-mail cadastrado)'}
""")
        else:
            st.warning("Não foi possível obter detalhes deste CNPJ agora.")

    # ── Exportar ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📥 Exportar lista de prospects")
    col_dl1, col_dl2 = st.columns(2)

    csv = df_vis.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    col_dl1.download_button("⬇️ Baixar CSV",
        csv, f"locvix_prospects_{cnae_final}.csv", "text/csv",
        use_container_width=True)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df_vis.to_excel(w, index=False, sheet_name="Prospects")
    col_dl2.download_button("⬇️ Baixar Excel",
        buf.getvalue(), f"locvix_prospects_{cnae_final}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTADO — CONSULTA POR CNPJ
# ══════════════════════════════════════════════════════════════════════════════
elif aba == "🏢 Consultar CNPJ" and btn_cnpj:

    cnpj_limpo = re.sub(r"\D", "", cnpj_input)
    if len(cnpj_limpo) != 14:
        st.error("CNPJ inválido — deve ter 14 dígitos.")
        st.stop()

    with st.spinner("Consultando CNPJ…"):
        det = buscar_cnpj(cnpj_limpo)

    if not det:
        st.error("CNPJ não encontrado ou serviço indisponível.")
        st.stop()

    emp = formatar(det)
    st.success(f"✅ {emp['Razão Social']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("CNPJ",             emp["CNPJ"])
    col1.metric("Razão Social",     emp["Razão Social"])
    col1.metric("Nome Fantasia",    emp["Nome Fantasia"] or "—")
    col1.metric("Situação",         emp["Situação"])
    col2.metric("Telefone 1",       emp["Telefone 1"] or "—")
    col2.metric("Telefone 2",       emp["Telefone 2"] or "—")
    col2.metric("E-mail",           emp["Email"] or "—")
    col2.metric("Data de Abertura", emp["Data de Abertura"] or "—")
    col3.metric("Município / UF",   f"{emp['Município']} / {emp['UF']}")
    col3.metric("Porte",            emp["Porte"] or "—")
    col3.metric("Capital Social",   emp["Capital Social"])
    col3.metric("Natureza Jurídica",emp["Natureza Jurídica"] or "—")

    st.divider()
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.subheader("📍 Endereço")
        st.write(f"**Logradouro:** {emp['Logradouro']}")
        st.write(f"**Bairro:** {emp['Bairro']}")
        st.write(f"**CEP:** {emp['CEP']}")
    with col_e2:
        st.subheader("🏭 Atividade")
        st.write(f"**CNAE Principal:** {emp['CNAE Principal']} — {emp['Descrição CNAE']}")
        secundarios = det.get("cnaes_secundarios") or []
        if secundarios:
            st.write("**CNAEs Secundários:**")
            for s in secundarios:
                st.write(f"- {s.get('codigo','')} — {s.get('descricao','')}")

    with st.expander("💡 Sugestão de abordagem comercial"):
        st.markdown(f"""
A **{emp['Razão Social']}** está localizada em **{emp['Município']} / {emp['UF']}**
e atua em **{emp['Descrição CNAE']}**.

**Como abordar:**
- Apresente a Locvix como especialista em locação de guindastes e maquinário pesado na região ES
- Destaque disponibilidade imediata, frota variada e suporte técnico
- Pergunte sobre próximas obras / paradas programadas / projetos de expansão
- Ofereça visita técnica sem compromisso

**Contato sugerido:**
📞 {emp['Telefone 1'] or emp['Telefone 2'] or '(sem telefone cadastrado)'}
📧 {emp['Email'] or '(sem e-mail cadastrado)'}
""")

    st.divider()
    buf2 = io.BytesIO()
    pd.DataFrame([emp]).to_excel(buf2, index=False, sheet_name="CNPJ")
    st.download_button("⬇️ Baixar Excel", buf2.getvalue(),
        f"locvix_cnpj_{cnpj_limpo}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)
