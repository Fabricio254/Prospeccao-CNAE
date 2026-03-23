import streamlit as st
import requests
import pandas as pd
import time
import re
import io
from urllib.parse import quote_plus

st.set_page_config(
    page_title="Prospecção de Clientes",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS customizado ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {font-size:2.2rem; font-weight:700; color:#1f77b4; margin-bottom:0.2rem;}
    .sub-title  {font-size:1rem; color:#555; margin-bottom:1.5rem;}
    .metric-card{background:#f0f4fa; border-radius:10px; padding:12px 18px; text-align:center;}
</style>
""", unsafe_allow_html=True)

# ── Tabela de CNAEs ────────────────────────────────────────────────────────────
CNAES = {
    "0111301": "Cultivo de trigo",
    "0115600": "Cultivo de soja",
    "0161001": "Atividade de apoio à agricultura",
    "0210101": "Cultivo de eucalipto",
    "1011201": "Frigorífico - abate de bovinos",
    "1012101": "Abate de suínos, aves e outros pequenos animais",
    "1031700": "Fabricação de conservas de frutas",
    "1094500": "Fabricação de massas alimentícias",
    "1111901": "Fabricação de aguardente de cana-de-açúcar",
    "1122401": "Fabricação de cervejas e chopes",
    "1220401": "Fabricação de cigarros",
    "1311100": "Preparação e fiação de fibras de algodão",
    "1412601": "Confecção de peças do vestuário",
    "1521100": "Fabricação de calçados de couro",
    "1610201": "Serrarias com desdobramento de madeira",
    "1621800": "Fabricação de esquadrias de madeira",
    "1710900": "Fabricação de celulose e outras pastas",
    "1722300": "Fabricação de produtos de papel",
    "1813001": "Impressão de jornais",
    "1921700": "Fabricação de products do refino de petróleo",
    "2011800": "Fabricação de cloro e álcalis",
    "2062200": "Fabricação de produtos de limpeza",
    "2091600": "Fabricação de adesivos e selantes",
    "2121101": "Fabricação de medicamentos para uso humano",
    "2211100": "Fabricação de pneumáticos e câmaras-de-ar",
    "2319200": "Fabricação de artigos de vidro",
    "2330301": "Fabricação de estruturas pré-moldadas de concreto",
    "2411300": "Produção de ferro-gusa",
    "2512800": "Fabricação de esquadrias de metal",
    "2531401": "Produção de forjados de aço",
    "2610800": "Fabricação de componentes eletrônicos",
    "2622100": "Fabricação de periféricos para equipamentos de informática",
    "2631100": "Fabricação de equipamentos transmissores de comunicação",
    "2710401": "Fabricação de geradores de corrente contínua e alternada",
    "2731700": "Fabricação de cabos de fibra ótica",
    "2812700": "Fabricação de equipamentos hidráulicos e pneumáticos",
    "2861500": "Fabricação de ferramentas",
    "2941700": "Fabricação de peças e acessórios para o sistema motor de veículos",
    "3011302": "Construção de embarcações para transporte",
    "3101200": "Fabricação de móveis com predominância de madeira",
    "3211601": "Lapidação de gemas",
    "3299001": "Fabricação de guarda-chuvas e similares",
    "3311200": "Manutenção e reparação de tanques, reservatórios metálicos",
    "3321000": "Instalação de máquinas industriais",
    "4110700": "Incorporação de empreendimentos imobiliários",
    "4120400": "Construção de edifícios",
    "4211101": "Construção de rodovias e ferrovias",
    "4221901": "Construção de barragens e represas",
    "4291000": "Obras portuárias e fluviais",
    "4311801": "Demolição de edifícios e outras estruturas",
    "4312600": "Perfurações e sondagens",
    "4321500": "Instalação e manutenção elétrica",
    "4322301": "Instalações hidráulicas, sanitárias e de gás",
    "4322302": "Instalação e manutenção de sistemas de ar condicionado",
    "4330401": "Impermeabilização em obras de engenharia civil",
    "4391600": "Obras de fundações",
    "4399101": "Administração de obras",
    "4511101": "Comércio a varejo de automóveis e camionetes novos",
    "4512901": "Representantes comerciais de veículos automotores",
    "4520001": "Manutenção e reparação mecânica de veículos",
    "4530703": "Comércio de peças e acessórios para veículos",
    "4541201": "Comércio de motocicletas novas",
    "4614100": "Representantes comerciais de máquinas e equipamentos",
    "4621400": "Comércio atacadista de café em grão",
    "4631100": "Comércio atacadista de leite e derivados",
    "4641901": "Comércio atacadista de tecidos",
    "4643501": "Comércio atacadista de calçados",
    "4711301": "Comércio varejista de mercadorias em geral",
    "4712100": "Mercearias e armazéns",
    "4721102": "Padaria e confeitaria com predominância de revenda",
    "4722901": "Comércio varejista de carnes - açougues",
    "4731800": "Comércio varejista de combustíveis",
    "4741500": "Comércio varejista de tintas e materiais para pintura",
    "4742300": "Comércio varejista de material elétrico",
    "4744001": "Comércio varejista de ferragens e ferramentas",
    "4751201": "Comércio varejista especializado de equipamentos de informática",
    "4754701": "Comércio varejista de móveis",
    "4771701": "Comércio varejista de produtos farmacêuticos",
    "4781400": "Comércio varejista de artigos do vestuário",
    "4789001": "Comércio varejista de suvenires e artesanatos",
    "4921301": "Transporte rodoviário coletivo de passageiros",
    "4930201": "Transporte rodoviário de carga",
    "4950700": "Trens turísticos, teleféricos e similares",
    "5011401": "Transporte marítimo de cabotagem",
    "5091201": "Transporte por navegação de travessia",
    "5111100": "Transporte aéreo de passageiros",
    "5211701": "Armazéns gerais",
    "5250801": "Agenciamento de cargas",
    "5310501": "Atividades do Correio Nacional",
    "5510801": "Hotéis",
    "5590601": "Albergues",
    "5611201": "Restaurantes e similares",
    "5620101": "Fornecimento de alimentos preparados",
    "5813100": "Edição de revistas",
    "5911101": "Estúdios cinematográficos",
    "6110801": "Serviços de telefonia fixa",
    "6120501": "Telefonia móvel celular",
    "6141800": "Operadoras de televisão por assinatura",
    "6201501": "Desenvolvimento de programas de computador sob encomenda",
    "6202300": "Desenvolvimento e licenciamento de programas customizáveis",
    "6203100": "Desenvolvimento de programas não-customizáveis",
    "6204000": "Consultoria em tecnologia da informação",
    "6209100": "Suporte técnico em tecnologia da informação",
    "6311900": "Tratamento de dados e provedores de serviços",
    "6420100": "Bancos comerciais",
    "6431000": "Bancos múltiplos com carteira comercial",
    "6911701": "Serviços advocatícios",
    "6920601": "Atividades de contabilidade",
    "7020400": "Consultoria em gestão empresarial",
    "7111100": "Serviços de arquitetura",
    "7112000": "Serviços de engenharia",
    "7119701": "Serviços de cartografia e topografia",
    "7210000": "Pesquisa em ciências físicas e naturais",
    "7311400": "Agências de publicidade",
    "7319003": "Marketing direto",
    "7410201": "Design gráfico",
    "7490101": "Serviços de tradução",
    "7490104": "Agenciamento de serviços e mão-de-obra",
    "7711000": "Locação de automóveis sem condutor",
    "7810800": "Seleção e agenciamento de mão-de-obra",
    "7911200": "Agências de viagens",
    "8011101": "Vigilância e segurança privada",
    "8020001": "Monitoramento de sistemas de segurança",
    "8111700": "Serviços combinados para apoio a edifícios",
    "8121400": "Limpeza em prédios e domicílios",
    "8122200": "Imunização e controle de pragas urbanas",
    "8129000": "Atividades de limpeza diversas",
    "8211300": "Serviços combinados de escritório",
    "8230001": "Organização de feiras, congressos e festas",
    "8291100": "Atividades de cobranças e informações cadastrais",
    "8511200": "Educação infantil - creche",
    "8513900": "Ensino fundamental",
    "8520100": "Ensino médio",
    "8531700": "Educação superior - graduação",
    "8591100": "Ensino de esportes",
    "8610101": "Atividades hospitalares",
    "8630501": "Atividade médica ambulatorial",
    "8640202": "Laboratórios clínicos",
    "8650001": "Atividades de enfermagem",
    "9512600": "Reparação de equipamentos de comunicação",
    "9601701": "Lavanderias",
    "9602501": "Cabeleireiros e manicure",
    "9603300": "Atividades funerárias",
}

ESTADOS = ["", "AC","AL","AP","AM","BA","CE","DF","ES","GO",
           "MA","MT","MS","MG","PA","PB","PR","PE","PI",
           "RJ","RN","RS","RO","RR","SC","SP","SE","TO"]


# ── Funções de API ─────────────────────────────────────────────────────────────

def buscar_por_cnae_casadosdados(cnae: str, municipio: str, estado: str, pagina: int = 1):
    """Busca empresas por CNAE na API pública da Casa dos Dados."""
    url = "https://api.casadosdados.com.br/v2/public/cnpj/pesquisa"
    payload = {
        "query": {
            "cnae_fiscal_principal": {"codigo": cnae},
            "situacao_cadastral": "ATIVA"
        },
        "range_query": {},
        "extras": {
            "somente_mei": False,
            "excluir_mei": False,
            "com_contato_telefonico": False,
            "com_email": False,
            "incluir_atividade_secundaria": False,
            "com_natureza_juridica": []
        },
        "page": pagina
    }
    if municipio.strip():
        payload["query"]["municipio"] = municipio.strip().upper()
    if estado.strip():
        payload["query"]["uf"] = estado.strip().upper()

    try:
        resp = requests.post(url, json=payload, timeout=20)
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("cnpj", [])
    except Exception:
        pass
    return []


def buscar_detalhes_cnpj(cnpj: str):
    """Busca dados completos de um CNPJ nas APIs públicas."""
    cnpj_limpo = re.sub(r"\D", "", cnpj)
    for url in [
        f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}",
        f"https://www.cnpj.ws/cnpj/{cnpj_limpo}",
        f"https://receitaws.com.br/v1/cnpj/{cnpj_limpo}",
    ]:
        try:
            resp = requests.get(url, timeout=12)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        time.sleep(0.3)
    return None


def formatar_empresa(emp: dict) -> dict:
    """Normaliza os campos de uma empresa para exibição."""
    tel = (emp.get("ddd_telefone_1") or "") + (emp.get("telefone_1") or "")
    tel2 = (emp.get("ddd_telefone_2") or "") + (emp.get("telefone_2") or "")
    cap = emp.get("capital_social") or 0
    try:
        cap_fmt = f"R$ {float(cap):,.2f}"
    except Exception:
        cap_fmt = str(cap)

    return {
        "CNPJ":             emp.get("cnpj", ""),
        "Razão Social":     emp.get("razao_social", ""),
        "Nome Fantasia":    emp.get("nome_fantasia", ""),
        "Situação":         emp.get("situacao_cadastral", ""),
        "Telefone 1":       tel,
        "Telefone 2":       tel2,
        "Email":            emp.get("email", ""),
        "Município":        emp.get("municipio", ""),
        "UF":               emp.get("uf", ""),
        "Logradouro":       f"{emp.get('logradouro','')} {emp.get('numero','')} {emp.get('complemento','')}".strip(),
        "Bairro":           emp.get("bairro", ""),
        "CEP":              emp.get("cep", ""),
        "Porte":            emp.get("porte", ""),
        "Natureza Jurídica":emp.get("natureza_juridica", ""),
        "Capital Social":   cap_fmt,
        "Data de Abertura": emp.get("data_inicio_atividade", ""),
        "CNAE Principal":   str(emp.get("cnae_fiscal", "")),
        "Descrição CNAE":   emp.get("cnae_fiscal_descricao", ""),
    }


# ── Interface ──────────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🔍 Prospecção de Clientes por CNAE</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Encontre empresas pelo código CNAE compatível com o seu negócio</p>', unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filtros de Busca")

    aba = st.radio("Modo:", ["Buscar por CNAE", "Consultar CNPJ"])

    if aba == "Buscar por CNAE":
        cnae_sel = st.selectbox(
            "CNAE:",
            options=list(CNAES.keys()),
            format_func=lambda x: f"{x} — {CNAES[x]}"
        )
        cnae_manual = st.text_input(
            "Ou digite o código manualmente:",
            placeholder="Ex: 6204000"
        )
        cnae_final = cnae_manual.strip() if cnae_manual.strip() else cnae_sel

        st.divider()
        municipio = st.text_input("Município:", placeholder="Ex: SAO PAULO")
        estado    = st.selectbox("Estado:", ESTADOS)
        paginas   = st.slider("Quantidade de páginas:", 1, 10, 2,
                              help="Cada página retorna até 20 empresas")

        st.divider()
        btn_buscar = st.button("🔍 Buscar Empresas", type="primary", use_container_width=True)

    else:
        cnpj_input = st.text_input("CNPJ:", placeholder="00.000.000/0001-00")
        btn_cnpj   = st.button("🔍 Consultar", type="primary", use_container_width=True)


# ── Resultado — Busca por CNAE ─────────────────────────────────────────────────
if aba == "Buscar por CNAE" and btn_buscar:
    desc_cnae = CNAES.get(cnae_final, cnae_final)
    st.info(f"**CNAE {cnae_final}** — {desc_cnae}")

    todas = []
    barra = st.progress(0, text="Iniciando busca...")

    for i, pg in enumerate(range(1, paginas + 1), 1):
        barra.progress(i / paginas, text=f"Buscando página {pg} de {paginas}…")
        resultado = buscar_por_cnae_casadosdados(cnae_final, municipio, estado, pg)
        todas.extend(resultado)
        if pg < paginas:
            time.sleep(0.8)

    barra.empty()

    if not todas:
        st.error(
            "Nenhuma empresa encontrada. Verifique o código CNAE, "
            "o município ou o estado e tente novamente."
        )
        st.stop()

    df = pd.DataFrame([formatar_empresa(e) for e in todas])

    # ── Métricas ───────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total encontrado",  len(df))
    c2.metric("Com telefone",      int((df["Telefone 1"] != "").sum()))
    c3.metric("Com e-mail",        int((df["Email"]      != "").sum()))
    c4.metric("Ativas",            int((df["Situação"]   == "ATIVA").sum()))

    st.divider()

    # ── Filtros rápidos ────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        apenas_ativas  = st.checkbox("Apenas ativas",        value=True)
    with col_f2:
        apenas_tel     = st.checkbox("Apenas com telefone",  value=False)
    with col_f3:
        apenas_email   = st.checkbox("Apenas com e-mail",    value=False)

    df_vis = df.copy()
    if apenas_ativas: df_vis = df_vis[df_vis["Situação"] == "ATIVA"]
    if apenas_tel:    df_vis = df_vis[df_vis["Telefone 1"] != ""]
    if apenas_email:  df_vis = df_vis[df_vis["Email"] != ""]

    st.markdown(f"**{len(df_vis)} empresas exibidas**")

    # ── Tabela interativa ──────────────────────────────────────────────────────
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
        }
    )

    # ── Detalhe de uma empresa ─────────────────────────────────────────────────
    st.divider()
    st.subheader("🔎 Ver detalhes de uma empresa")
    cnpjs_disponiveis = df_vis["CNPJ"].dropna().unique().tolist()
    cnpj_escolhido = st.selectbox("Selecione o CNPJ para ver dados completos:", [""] + cnpjs_disponiveis)

    if cnpj_escolhido:
        with st.spinner("Carregando dados completos..."):
            detalhe = buscar_detalhes_cnpj(cnpj_escolhido)

        if detalhe:
            emp = formatar_empresa(detalhe)
            col1, col2, col3 = st.columns(3)
            col1.metric("Razão Social",     emp["Razão Social"])
            col1.metric("Nome Fantasia",    emp["Nome Fantasia"] or "—")
            col1.metric("Situação",         emp["Situação"])
            col2.metric("Telefone 1",       emp["Telefone 1"] or "—")
            col2.metric("Telefone 2",       emp["Telefone 2"] or "—")
            col2.metric("E-mail",           emp["Email"] or "—")
            col3.metric("Município / UF",   f"{emp['Município']} / {emp['UF']}")
            col3.metric("Porte",            emp["Porte"] or "—")
            col3.metric("Capital Social",   emp["Capital Social"])

            with st.expander("📋 Todos os campos"):
                for k, v in emp.items():
                    st.write(f"**{k}:** {v}")
        else:
            st.warning("Não foi possível obter os detalhes deste CNPJ no momento.")

    # ── Download ───────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📥 Exportar resultados")
    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        csv_bytes = df_vis.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="⬇️ Baixar CSV",
            data=csv_bytes,
            file_name=f"prospeccao_cnae_{cnae_final}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_dl2:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_vis.to_excel(writer, index=False, sheet_name="Empresas")
        st.download_button(
            label="⬇️ Baixar Excel",
            data=buf.getvalue(),
            file_name=f"prospeccao_cnae_{cnae_final}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )


# ── Resultado — Consulta de CNPJ ───────────────────────────────────────────────
elif aba == "Consultar CNPJ" and btn_cnpj:
    cnpj_limpo = re.sub(r"\D", "", cnpj_input)
    if len(cnpj_limpo) != 14:
        st.error("CNPJ inválido! Deve conter exatamente 14 dígitos.")
        st.stop()

    with st.spinner("Consultando CNPJ..."):
        detalhe = buscar_detalhes_cnpj(cnpj_limpo)

    if not detalhe:
        st.error("CNPJ não encontrado ou serviço indisponível no momento.")
        st.stop()

    emp = formatar_empresa(detalhe)
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
    st.subheader("📋 Endereço")
    st.write(f"**Logradouro:** {emp['Logradouro']}")
    st.write(f"**Bairro:** {emp['Bairro']}")
    st.write(f"**CEP:** {emp['CEP']}")

    st.divider()
    st.subheader("📋 Atividade")
    st.write(f"**CNAE Principal:** {emp['CNAE Principal']} — {emp['Descrição CNAE']}")

    # CNAEs secundários (quando disponível)
    secundarios = detalhe.get("cnaes_secundarios") or []
    if secundarios:
        st.write("**CNAEs Secundários:**")
        for s in secundarios:
            codigo = s.get("codigo") or s.get("cnae", "")
            desc   = s.get("descricao") or s.get("descricao", "")
            st.write(f"- {codigo} — {desc}")

    # Export individual
    st.divider()
    buf2 = io.BytesIO()
    pd.DataFrame([emp]).to_excel(buf2, index=False, sheet_name="CNPJ")
    st.download_button(
        "⬇️ Baixar dados em Excel",
        buf2.getvalue(),
        f"cnpj_{cnpj_limpo}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
