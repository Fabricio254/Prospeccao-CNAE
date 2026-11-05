import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import time
import re
import io
import base64
from pathlib import Path

_LOGO_DATA_URI = "data:image/svg+xml;base64," + base64.b64encode(
    Path(__file__).with_name("zampasys_logo.svg").read_bytes()
).decode("ascii")

st.set_page_config(
    page_title="ZampaSys — Prospecção de Clientes",
    page_icon=str(Path(__file__).with_name("zampasys_icon.png")),
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Autenticação ──────────────────────────────────────────────────────────────
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
    <style>
        /* Empurra o conteúdo para o centro vertical da tela */
        [data-testid="stAppViewContainer"] > .main > .block-container {
            padding-top: 8vh !important;
            padding-bottom: 0 !important;
        }
        /* Remove o gap entre elementos da coluna central (une cabeçalho + form) */
        [data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlock"] {
            gap: 0 !important;
        }
        /* Topo do card — cantos superiores arredondados */
        .lv-head {
            background: #ffffff;
            border-radius: 16px 16px 0 0;
            padding: 2.5rem 2rem 1rem 2rem;
            text-align: center;
            box-shadow: 0 -4px 30px rgba(0,0,0,.09),
                         4px 0 12px rgba(0,0,0,.05),
                        -4px 0 12px rgba(0,0,0,.05);
        }
        .lv-logo  { display: block; width: min(100%, 250px); height: auto;
                    margin: 0 auto 0.75rem; }
        .lv-sub   { font-size: 0.875rem; color: #999; margin: 0 0 0.8rem 0; }
        .lv-hr    { border: none; border-top: 1px solid #efefef; margin: 0; }
        /* Base do card — cantos inferiores arredondados */
        [data-testid="stForm"] {
            background: #ffffff !important;
            border: none !important;
            border-radius: 0 0 16px 16px !important;
            padding: 1.2rem 1.5rem 1.8rem 1.5rem !important;
            box-shadow:  4px 8px 30px rgba(0,0,0,.09),
                        -4px 0  12px rgba(0,0,0,.05) !important;
        }
        /* Remove borda interna padrão do st.form */
        [data-testid="stFormBorderWrapper"] {
            border: none !important;
            padding: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
    _, col_c, _ = st.columns([1, 1, 1])
    with col_c:
        st.markdown(f"""
        <div class="lv-head">
            <img class="lv-logo" src="{_LOGO_DATA_URI}" alt="ZampaSys">
            <p class="lv-sub">Prospecção de Clientes</p>
            <hr class="lv-hr">
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            senha = st.text_input("", type="password", placeholder="Digite a senha…")
            submitted = st.form_submit_button("Entrar", type="primary",
                                              use_container_width=True)
        if submitted:
            if senha == "zampa":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()


st.markdown("""
<style>
    .main-title {font-size:2.2rem; font-weight:700; color:#e67e22; margin-bottom:0.2rem;}
    .sub-title  {font-size:1rem; color:#555; margin-bottom:1.5rem;}
    .tag-seg    {background:#fff3e0; border-left:4px solid #e67e22; padding:8px 14px;
                 border-radius:4px; font-size:.9rem; margin-bottom:.8rem;}
    /* Esconde toolbar superior (Share, editar, GitHub, Deploy) — mantém o header no DOM */
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    header[data-testid="stHeader"] {background: transparent !important; border-bottom: none !important;}
    #MainMenu {display: none !important;}
    footer {display: none !important;}

    /* ── Botão flutuante claro/escuro — lado DIREITO ── */
    #locvix-theme-btn {
        position: fixed; right: 16px; bottom: 88px;
        width: 46px; height: 46px; border-radius: 50%;
        border: 2px solid #ddd; background: #f0f0f0;
        font-size: 22px; cursor: pointer; z-index: 99999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.18);
        transition: transform 0.2s; padding: 0;
        display: flex; align-items: center; justify-content: center;
    }
    #locvix-theme-btn:hover { transform: scale(1.12); }

    /* ── Sidebar sempre aberta — esconde botão de colapsar ── */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] {
        transform: translateX(0) !important;
        visibility: visible !important;
        display: block !important;
    }
    section[data-testid="stSidebar"] {
        width: 21rem !important;
        min-width: 21rem !important;
        flex-shrink: 0 !important;
    }
    /* Esconde TODOS os botões de colapsar/expandir sidebar */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"],
    button[aria-label*="idebar"],
    button[aria-label*="ollapse"],
    button[aria-label*="xpand"] {
        display: none !important;
    }

    /* ── Dark mode ── */
    body[data-theme="dark"] { color-scheme: dark; }
    body[data-theme="dark"] .stApp,
    body[data-theme="dark"] [data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important; color: #e0e0e0 !important;
    }
    body[data-theme="dark"] .main .block-container { background-color: #0e1117 !important; }
    body[data-theme="dark"] section[data-testid="stSidebar"],
    body[data-theme="dark"] section[data-testid="stSidebar"] > div {
        background-color: #1a1c24 !important; color: #e0e0e0 !important;
    }
    body[data-theme="dark"] p, body[data-theme="dark"] h1, body[data-theme="dark"] h2,
    body[data-theme="dark"] h3, body[data-theme="dark"] h4, body[data-theme="dark"] label,
    body[data-theme="dark"] .stMarkdown, body[data-theme="dark"] small {
        color: #e0e0e0 !important;
    }
    body[data-theme="dark"] input, body[data-theme="dark"] textarea {
        background-color: #262730 !important; color: #fafafa !important;
        border-color: #555 !important;
    }
    /* BaseWeb — fundo e COR DO TEXTO dos campos input/select/multiselect */
    body[data-theme="dark"] [data-baseweb="select"] > div,
    body[data-theme="dark"] [data-baseweb="input"] > div {
        background-color: #262730 !important; border-color: #555 !important;
        color: #fafafa !important;
    }
    /* Texto digitado e valor selecionado dentro de qualquer campo */
    body[data-theme="dark"] [data-baseweb="select"] span,
    body[data-theme="dark"] [data-baseweb="select"] div,
    body[data-theme="dark"] [data-baseweb="input"] span,
    body[data-theme="dark"] [data-baseweb="input"] input,
    body[data-theme="dark"] [data-baseweb="textarea"] textarea {
        color: #fafafa !important;
        background-color: transparent !important;
    }
    /* Placeholder */
    body[data-theme="dark"] [data-baseweb="select"] input::placeholder,
    body[data-theme="dark"] [data-baseweb="input"] input::placeholder {
        color: #888 !important;
    }
    /* Tags do multiselect — vermelho igual ao light mode */
    body[data-theme="dark"] [data-baseweb="tag"] {
        background-color: #e53935 !important;
        border-color: #c62828 !important;
    }
    body[data-theme="dark"] [data-baseweb="tag"] span,
    body[data-theme="dark"] [data-baseweb="tag"] button {
        color: #ffffff !important;
    }
    /* Lista suspensa do dropdown */
    body[data-theme="dark"] [data-baseweb="popover"],
    body[data-theme="dark"] [data-baseweb="menu"] {
        background-color: #1e2030 !important;
    }
    body[data-theme="dark"] [data-baseweb="menu"] li,
    body[data-theme="dark"] [data-baseweb="menu"] li span,
    body[data-theme="dark"] [role="option"] {
        color: #e0e0e0 !important;
        background-color: #1e2030 !important;
    }
    body[data-theme="dark"] [data-baseweb="menu"] li:hover,
    body[data-theme="dark"] [role="option"]:hover {
        background-color: #2a2e42 !important;
    }
    /* Radio buttons e sliders */
    body[data-theme="dark"] [data-testid="stRadio"] label,
    body[data-theme="dark"] [data-testid="stSlider"] label,
    body[data-theme="dark"] [data-testid="stNumberInput"] label {
        color: #e0e0e0 !important;
    }
    body[data-theme="dark"] [data-testid="stNumberInput"] input {
        color: #fafafa !important; background-color: #262730 !important;
    }
    body[data-theme="dark"] [data-testid="stMetricValue"],
    body[data-theme="dark"] [data-testid="stMetricLabel"] { color: #e0e0e0 !important; }
    body[data-theme="dark"] hr { border-color: #333 !important; }
    body[data-theme="dark"] .stExpander summary { color: #e0e0e0 !important; }
    body[data-theme="dark"] .tag-seg {
        background: #1f1500 !important; color: #ffcf7d !important;
    }
    body[data-theme="dark"] .sub-title { color: #999 !important; }
    body[data-theme="dark"] #locvix-theme-btn {
        background: #262730 !important; border-color: #555 !important;
    }
    /* Link buttons (st.link_button) no dark mode — secundários */
    body[data-theme="dark"] [data-testid="stLinkButton"] a {
        background-color: #262730 !important;
        color: #e0e0e0 !important;
        border-color: #555 !important;
    }
    body[data-theme="dark"] [data-testid="stLinkButton"] a:hover {
        background-color: #2a2e42 !important;
        color: #ffffff !important;
        border-color: #888 !important;
    }
    /* Garante que o texto interno também seja claro */
    body[data-theme="dark"] [data-testid="stLinkButton"] a p,
    body[data-theme="dark"] [data-testid="stLinkButton"] a span {
        color: #e0e0e0 !important;
    }
    /* Download buttons (st.download_button) no dark mode — secundários */
    body[data-theme="dark"] [data-testid="stDownloadButton"] button {
        background-color: #262730 !important;
        color: #e0e0e0 !important;
        border-color: #555 !important;
    }
    body[data-theme="dark"] [data-testid="stDownloadButton"] button:hover {
        background-color: #2a2e42 !important;
        color: #ffffff !important;
        border-color: #888 !important;
    }
    body[data-theme="dark"] [data-testid="stDownloadButton"] button p,
    body[data-theme="dark"] [data-testid="stDownloadButton"] button span {
        color: #e0e0e0 !important;
    }
    /* Botões secundários genéricos (st.button sem type="primary") */
    body[data-theme="dark"] [data-testid="stButton"] button[kind="secondary"],
    body[data-theme="dark"] [data-testid="stBaseButton-secondary"] {
        background-color: #262730 !important;
        color: #e0e0e0 !important;
        border-color: #555 !important;
    }
</style>
<button id="locvix-theme-btn" title="Alternar tema claro/escuro">🌙</button>
""", unsafe_allow_html=True)

components.html("""
<script>
(function(){
    var KEY = 'locvix-theme';
    function applyTheme(theme) {
        try {
            var p = window.parent;
            p.localStorage.setItem(KEY, theme);
            p.document.body.setAttribute('data-theme', theme);
            var btn = p.document.getElementById('locvix-theme-btn');
            if (btn) btn.textContent = theme === 'dark' ? '\\u2600\\uFE0F' : '\\uD83C\\uDF19';
        } catch(e) {}
    }
    function toggleTheme() {
        try {
            var cur = window.parent.localStorage.getItem(KEY) || 'light';
            applyTheme(cur === 'dark' ? 'light' : 'dark');
        } catch(e) {}
    }
    function bindBtn() {
        try {
            var btn = window.parent.document.getElementById('locvix-theme-btn');
            if (btn && !btn._lbound) {
                btn.addEventListener('click', toggleTheme);
                btn._lbound = true;
            }
        } catch(e) {}
    }
    applyTheme(window.parent.localStorage.getItem(KEY) || 'light');
    bindBtn();

    // ── MutationObserver permanente para manter sidebar sempre aberta ──
    (function() {
        try {
            var p = window.parent;
            function forceOpen() {
                var targets = [
                    p.document.querySelector('section[data-testid="stSidebar"]'),
                    p.document.querySelector('[data-testid="stSidebarContent"]'),
                ];
                targets.forEach(function(el) {
                    if (!el) return;
                    el.style.setProperty('transform', 'translateX(0)', 'important');
                    el.style.setProperty('visibility', 'visible', 'important');
                });
                var sb = targets[0];
                if (sb) {
                    sb.style.setProperty('width', '21rem', 'important');
                    sb.style.setProperty('min-width', '21rem', 'important');
                    // Observe all children too
                    Array.from(sb.children).forEach(function(child) {
                        child.style.setProperty('transform', 'translateX(0)', 'important');
                        child.style.setProperty('visibility', 'visible', 'important');
                    });
                }
            }
            forceOpen();
            var obs = new p.MutationObserver(forceOpen);
            function attachObs() {
                var sb = p.document.querySelector('section[data-testid="stSidebar"]');
                if (sb) obs.observe(sb, { attributes: true, subtree: true, attributeFilter: ['style', 'class'] });
            }
            attachObs();
            // Re-attach after Streamlit re-renders
            setInterval(function() {
                try { forceOpen(); attachObs(); } catch(e) {}
            }, 500);
        } catch(e) {}
    })();

    setInterval(function() {
        try {
            var p = window.parent;
            var theme = p.localStorage.getItem(KEY) || 'light';
            if (p.document.body.getAttribute('data-theme') !== theme) {
                p.document.body.setAttribute('data-theme', theme);
            }
            var tBtn = p.document.getElementById('locvix-theme-btn');
            if (tBtn) {
                var expected = theme === 'dark' ? '\\u2600\\uFE0F' : '\\uD83C\\uDF19';
                if (tBtn.textContent !== expected) tBtn.textContent = expected;
                if (!tBtn._lbound) { tBtn.addEventListener('click', toggleTheme); tBtn._lbound = true; }
            }
            // Força tags do multiselect para vermelho no dark mode
            if (theme === 'dark') {
                p.document.querySelectorAll('[data-baseweb="tag"]').forEach(function(tag) {
                    tag.style.setProperty('background-color', '#e53935', 'important');
                    tag.style.setProperty('border-color', '#c62828', 'important');
                    tag.querySelectorAll('span, button, svg').forEach(function(child) {
                        child.style.setProperty('color', '#ffffff', 'important');
                        child.style.setProperty('fill', '#ffffff', 'important');
                    });
                });
            }
        } catch(e) {}
    }, 300);
})();
</script>
""", height=0, scrolling=False)

# ══════════════════════════════════════════════════════════════════════════════
# GRUPOS DE CNAE — exemplos de setores para busca de empresas
# ══════════════════════════════════════════════════════════════════════════════
GRUPOS_CNAE = {

    "🏗️ Construção Civil e Obras": {
        "desc": "Empresas de construção, infraestrutura e serviços especializados.",
        "cnaes": {
            "4120400": "Construção de edifícios",
            "4211101": "Construção de rodovias e ferrovias",
            "4221901": "Construção de barragens e represas",
            "4222701": "Construção de redes de abastecimento de água",
            "4223500": "Construção de redes de transportes por dutos",
            "4291000": "Obras portuárias, marítimas e fluviais",
            "4292801": "Montagem de estruturas metálicas",
            "4311801": "Demolição de edifícios e outras estruturas",
            "4322301": "Instalações hidráulicas, sanitárias e de gás",
            "4391600": "Obras de fundações",
            "4399103": "Obras de terraplanagem",
        }
    },

    "🏭 Indústria — Manutenção e Instalação": {
        "desc": "Empresas de fabricação, instalações e manutenção industrial.",
        "cnaes": {
            "3311200": "Manutenção de tanques e reservatórios metálicos",
            "3312102": "Manutenção e reparação de equipamentos para a indústria",
            "3313901": "Manutenção de geradores, transformadores e motores",
            "3314701": "Manutenção de máquinas motrizes não elétricas",
            "3314799": "Manutenção e reparação de outras máquinas e equipamentos",
            "2710401": "Fabricação de geradores de corrente contínua e alternada",
            "2812700": "Fabricação de equipamentos hidráulicos e pneumáticos",
            "2330301": "Fabricação de estruturas pré-moldadas de concreto",
            "1710900": "Fabricação de celulose e outras pastas",
            "1921700": "Fabricação de produtos do refino de petróleo",
        }
    },

    "⚡ Energia — Eólica, Elétrica, Óleo e Gás": {
        "desc": "Empresas de geração de energia e atividades ligadas a óleo e gás.",
        "cnaes": {
            "3511501": "Geração de energia elétrica",
            "3511502": "Geração de energia elétrica de origem eólica",
            "3511503": "Geração de energia elétrica solar fotovoltaica",
            "0600001": "Extração de petróleo e gás natural",
            "0910600": "Atividades de apoio à extração de petróleo e gás",
        }
    },

    "⛏️ Mineração e Siderurgia": {
        "desc": "Empresas de extração mineral, siderurgia e metalurgia.",
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

    "🚛 Transporte e Logística": {
        "desc": "Empresas de transporte, terminais e agenciamento de cargas.",
        "cnaes": {
            "5231101": "Administração de portos e terminais",
            "5250801": "Agenciamento de cargas",
        }
    },

    "🌾 Agroindústria e Alimentos": {
        "desc": "Empresas ligadas à produção agroindustrial e de alimentos.",
        "cnaes": {
            "1011201": "Frigorífico — abate de bovinos",
        }
    },

    "🎪 Eventos, Palcos e Estruturas Temporárias": {
        "desc": "Empresas de organização de eventos e serviços relacionados.",
        "cnaes": {
            "8230001": "Organização de feiras, congressos, exposições e festas",
            "9001906": "Atividades de sonorização e de iluminação",
            "4292801": "Montagem de estruturas metálicas",
        }
    },

    "🏢 Portos e Terminais": {
        "desc": "Empresas de operação portuária, terminais e serviços marítimos.",
        "cnaes": {
            "5231101": "Administração de portos e terminais",
            "5231102": "Operações de terminais",
            "5231103": "Gestão de terminais aquaviários",
            "5232000": "Atividades de agenciamento marítimo",
            "4291000": "Obras portuárias, marítimas e fluviais",
            "0600001": "Extração de petróleo e gás natural",
            "0910600": "Atividades de apoio à extração de petróleo e gás",
        }
    },

    "🏛️ Engenharia Civil e Arquitetura": {
        "desc": "Empresas de engenharia, arquitetura e serviços técnicos relacionados.",
        "cnaes": {
            "7112000": "Serviços de engenharia",
            "7111100": "Serviços de arquitetura",
            "7119701": "Serviços de cartografia e topografia",
            "7119703": "Serviços de desenho técnico",
            "4311801": "Demolição de edifícios e outras estruturas",
            "4319300": "Serviços de preparação do terreno",
            "4221901": "Construção de barragens e represas",
            "4213800": "Obras de urbanização — ruas, praças e calçadas",
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

def buscar_por_cnae(cnae: str, municipio: str, estado: str, cursor: int | None, _token: str = ""):
    """Busca empresas por CNAE via minhareceita.org (dados abertos da Receita Federal)."""
    url = "https://minhareceita.org/"
    params: dict = {"cnae": cnae}
    if estado.strip():
        params["uf"] = estado.strip().upper()
    if cursor:
        params["cursor"] = cursor

    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    for tentativa in range(3):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=30)
            if r.status_code == 200:
                data = r.json()
                empresas = data.get("data", [])
                # Filtra por município localmente (a API filtra só por UF)
                if municipio.strip():
                    mun_upper = municipio.strip().upper()
                    empresas = [e for e in empresas if e.get("municipio", "").upper() == mun_upper]
                next_cursor = data.get("cursor")
                return empresas, next_cursor, None
            if r.status_code in (429, 503):
                time.sleep(3 * (tentativa + 1))
                continue
            return [], None, f"HTTP {r.status_code}: {r.text[:300]}"
        except Exception as e:
            time.sleep(2)
    return [], None, "Timeout ou erro de conexão após 3 tentativas"


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


def _str(obj, key="descricao"):
    if obj is None:
        return ""
    if isinstance(obj, dict):
        return str(obj.get(key) or obj.get("nome") or obj.get("sigla") or "")
    return str(obj)


def formatar_brasilio(emp: dict) -> dict:
    """Normaliza resposta da Brasil.io para o formato padrão da tabela."""
    tel1 = (emp.get("ddd1") or "") + (emp.get("telefone1") or "")
    tel2 = (emp.get("ddd2") or "") + (emp.get("telefone2") or "")
    cap  = emp.get("capital_social") or 0
    try:    cap_fmt = f"R$ {float(str(cap).replace(',', '.')):,.2f}"
    except: cap_fmt = str(cap)
    return {
        "CNPJ":              emp.get("cnpj", ""),
        "Razão Social":      emp.get("razao_social", ""),
        "Nome Fantasia":     emp.get("nome_fantasia", ""),
        "Situação":          emp.get("situacao_cadastral", ""),
        "Telefone 1":        tel1,
        "Telefone 2":        tel2,
        "Email":             emp.get("email", ""),
        "Município":         emp.get("municipio", ""),
        "UF":                emp.get("uf", ""),
        "Logradouro":        f"{emp.get('logradouro','') or ''} {emp.get('numero','') or ''} {emp.get('complemento','') or ''}".strip(),
        "Bairro":            emp.get("bairro", ""),
        "CEP":               emp.get("cep", ""),
        "Porte":             emp.get("porte", ""),
        "Natureza Jurídica": emp.get("natureza_juridica", ""),
        "Capital Social":    cap_fmt,
        "Data de Abertura":  emp.get("data_inicio_atividade", ""),
        "CNAE Principal":    str(emp.get("cnae_fiscal", "")),
        "Descrição CNAE":    emp.get("cnae_fiscal_descricao", ""),
    }


def formatar(emp: dict) -> dict:
    """Normaliza resposta da BrasilAPI / ReceitaWS / minhareceita para o formato padrão."""
    tel  = (emp.get("ddd_telefone_1") or "") + (emp.get("telefone_1") or "")
    tel2 = (emp.get("ddd_telefone_2") or "") + (emp.get("telefone_2") or "")
    cap  = emp.get("capital_social") or 0
    try:    cap_fmt = f"R$ {float(cap):,.2f}"
    except: cap_fmt = str(cap)

    # minhareceita retorna situacao_cadastral como int; BrasilAPI retorna string
    _SIT_MAP = {1: "NULA", 2: "ATIVA", 3: "SUSPENSA", 4: "INAPTA", 8: "BAIXADA"}
    sit_raw = emp.get("situacao_cadastral", "")
    if isinstance(sit_raw, int):
        situacao = _SIT_MAP.get(sit_raw, str(sit_raw))
    else:
        situacao = emp.get("descricao_situacao_cadastral") or str(sit_raw)

    # minhareceita agrupa telefone no campo ddd_telefone_1 sem separação de DDD
    tel_raw = emp.get("ddd_telefone_1") or ""
    if tel_raw and not tel:
        tel = tel_raw

    return {
        "CNPJ":              emp.get("cnpj", ""),
        "Razão Social":      emp.get("razao_social", ""),
        "Nome Fantasia":     emp.get("nome_fantasia", ""),
        "Situação":          situacao,
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


def buscar_google_maps(termo: str, cidade: str, estado: str, api_key: str, proximo_token: str = None):
    """Busca estabelecimentos via Google Maps Places Text Search API."""
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    if proximo_token:
        params = {"pagetoken": proximo_token, "key": api_key}
    else:
        localizacao = ", ".join(p for p in (cidade, estado, "Brasil") if p)
        params = {
            "query":    f"{termo} em {localizacao}",
            "key":      api_key,
            "language": "pt-BR",
            "region":   "br",
        }
    try:
        r = requests.get(url, params=params, timeout=20)
        if r.status_code == 200:
            data = r.json()
            return data.get("results", []), data.get("next_page_token")
    except Exception:
        pass
    return [], None


def sugestao_abordagem(emp: dict, nome_empresa: str, oferta_empresa: str, desc: str = "") -> str:
    """Monta uma abordagem comercial aplicável a qualquer setor."""
    setor = emp.get("Descrição CNAE") or desc or "atividade não informada"
    apresentacao = nome_empresa.strip() or "sua empresa"
    oferta = oferta_empresa.strip() or "seus produtos ou serviços"
    return f"""
A **{emp['Razão Social']}** atua em **{setor}** e está localizada em
**{emp['Município']} / {emp['UF']}**.

**Como abordar:**
- Apresente {apresentacao} e explique como {oferta} pode atender à empresa.
- Pergunte sobre necessidades atuais, prioridades e critérios de compra.
- Relacione sua oferta a uma necessidade identificada.
- Combine um próximo passo, como reunião, demonstração ou proposta.

**Contato sugerido:**
📞 {emp['Telefone 1'] or emp['Telefone 2'] or '(sem telefone cadastrado)'}
📧 {emp['Email'] or '(sem e-mail cadastrado)'}
"""


# ══════════════════════════════════════════════════════════════════════════════
# INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f'<p class="main-title"><img src="{_LOGO_DATA_URI}" alt="ZampaSys" style="height:48px;vertical-align:middle;margin-right:8px"> — Prospecção de Clientes</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Encontre empresas por setor, CNAE, CNPJ ou localização para novas oportunidades de negócio.</p>', unsafe_allow_html=True)
st.markdown('<p style="font-size:0.78rem; color:#888; margin-top:-0.8rem; margin-bottom:1rem;">Desenvolvido por Fabrício Zamprogno</p>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filtros de Busca")

    st.caption("📡 Dados: minhareceita.org (Receita Federal — gratuito, sem token)")
    with st.expander("🏢 Personalizar abordagem (opcional)"):
        nome_empresa = st.text_input("Nome da sua empresa:", placeholder="Ex: ZampaSys")
        oferta_empresa = st.text_input("Produto ou serviço oferecido:", placeholder="Ex: soluções de gestão")
    st.divider()
    aba = st.radio("Modo:", ["🔍 Buscar por Segmento / CNAE", "🏢 Consultar CNPJ", "🗺️ Google Maps"])

    if aba == "🔍 Buscar por Segmento / CNAE":

        modo = st.radio(
            "Selecionar CNAE por:",
            ["✏️ Informar CNAEs", "🎯 Segmentos sugeridos"]
        )

        if modo == "🎯 Segmentos sugeridos":
            segmento = st.selectbox("Setor de atividade:", list(GRUPOS_CNAE.keys()))
            cnaes_seg = GRUPOS_CNAE[segmento]["cnaes"]
            st.markdown(
                f'<div class="tag-seg">📌 {GRUPOS_CNAE[segmento]["desc"]}</div>',
                unsafe_allow_html=True
            )
            cnae_final = st.multiselect(
                "CNAEs selecionados:",
                list(cnaes_seg.keys()),
                default=list(cnaes_seg.keys()),
                format_func=lambda x: f"{x} — {cnaes_seg[x]}",
                help="Desmarque os CNAEs que não deseja incluir."
            )
            if not cnae_final:
                st.warning("Selecione ao menos um CNAE.")
        else:
            segmento = "CNAEs informados"
            codigos_cnae = st.text_input(
                "CNAEs (separados por vírgula):",
                placeholder="Ex: 6201501, 4711302",
                help="Informe um ou mais códigos CNAE de 7 dígitos."
            )
            cnae_final = list(dict.fromkeys(
                codigo.strip() for codigo in codigos_cnae.split(",") if codigo.strip()
            ))
            if not cnae_final:
                st.info("Informe ao menos um CNAE para iniciar a busca.")

        st.divider()
        municipio = st.text_input("Município:", placeholder="Opcional: cidade")
        estado = st.selectbox("Estado:", ESTADOS, format_func=lambda uf: uf or "Todos os estados")
        paginas = st.slider("Páginas de resultado:", 1, 10, 3,
                            help="Cada página = até 20 empresas")
        st.divider()
        btn_buscar = st.button("🔍 Buscar Empresas", type="primary", use_container_width=True)

    elif aba == "🏢 Consultar CNPJ":
        cnpj_input = st.text_input("CNPJ:", placeholder="00.000.000/0001-00")
        btn_cnpj   = st.button("🔍 Consultar", type="primary", use_container_width=True)

    else:  # Google Maps
        st.markdown("**🗺️ Busca no Google Maps**")
        maps_api_key = st.text_input(
            "Chave API Google Maps (opcional):",
            type="password",
            help="Sem chave: abre links de busca. Com a Places API Key: mostra resultados aqui no app."
        )

        TERMOS_MAPS = {
            "✏️ Personalizado":             None,
            "🛒 Comércio e varejo":         "lojas e comércio",
            "🩺 Saúde":                     "clínicas e serviços de saúde",
            "🎓 Educação":                  "escolas e cursos",
            "💻 Tecnologia":                "empresas de tecnologia",
            "🍽️ Alimentação":              "restaurantes e alimentação",
            "🏢 Serviços profissionais":    "empresas de serviços profissionais",
            "🏭 Indústria":                 "indústrias",
            "🏗️ Construção":               "construtoras",
            "🚛 Transporte e logística":    "transportadoras e logística",
            "🌾 Agronegócio":               "empresas do agronegócio",
        }

        maps_categoria = st.selectbox("Categoria:", list(TERMOS_MAPS.keys()))

        if TERMOS_MAPS[maps_categoria] is None:
            maps_termo = st.text_input(
                "Termo de busca:", placeholder="Ex: clínicas odontológicas, lojas de móveis"
            ).strip()
        else:
            maps_termo = TERMOS_MAPS[maps_categoria]
            st.caption(f"🔎 Buscando: *{maps_termo}*")

        st.divider()
        municipio_maps = st.text_input("Cidade:", placeholder="Opcional: cidade")
        estado_maps = st.selectbox(
            "Estado:", ESTADOS, key="estado_maps",
            format_func=lambda uf: uf or "Todos os estados"
        )
        paginas_maps = st.slider("Páginas (API Key):", 1, 5, 2,
                                 help="Cada página = até 20 resultados. Requer API Key.")
        st.divider()
        btn_maps = st.button("🗺️ Buscar no Maps", type="primary", use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTADO — BUSCA POR CNAE
# ══════════════════════════════════════════════════════════════════════════════
if aba == "🔍 Buscar por Segmento / CNAE" and btn_buscar:

    cnaes_buscar = list(cnae_final)

    if not cnaes_buscar:
        st.error("Selecione ou informe um CNAE antes de buscar.")
        st.stop()
    if municipio.strip() and not estado:
        st.error("Selecione o estado ao informar um município.")
        st.stop()
    invalidos = [codigo for codigo in cnaes_buscar if not re.fullmatch(r"\d{7}", codigo)]
    if invalidos:
        st.error("Informe códigos CNAE com exatamente 7 dígitos, separados por vírgula.")
        st.stop()

    if len(cnaes_buscar) == 1:
        desc = TODOS_CNAES.get(cnaes_buscar[0], cnaes_buscar[0])
        st.info(f"**CNAE {cnaes_buscar[0]}** — {desc}")
        nome_export = cnaes_buscar[0]
    else:
        desc = segmento
        st.info(f"🔍 Buscando **{len(cnaes_buscar)} CNAEs** do segmento **{segmento}**")
        nome_export = re.sub(r"[^\w-]+", "_", segmento).strip("_")[:30]

    todas = []
    erros_api: list = []
    vistos: set = set()
    total_cnaes = len(cnaes_buscar)
    barra = st.progress(0, text="Iniciando busca…")
    for idx_c, cnae_iter in enumerate(cnaes_buscar):
        cursor = None
        for pg in range(1, paginas + 1):
            progresso = (idx_c * paginas + pg) / (total_cnaes * paginas)
            barra.progress(progresso, text=f"CNAE {cnae_iter} — página {pg}/{paginas}…")
            resultados, cursor, erro = buscar_por_cnae(cnae_iter, municipio, estado, cursor)
            todas.extend(resultados)
            if erro:
                erros_api.append(f"CNAE {cnae_iter} p.{pg}: {erro}")
            if not cursor:
                break  # sem mais páginas para este CNAE
            time.sleep(0.8)
    barra.empty()

    if erros_api:
        with st.expander(f"⚠️ {len(erros_api)} erro(s) de API — clique para ver"):
            for e in erros_api:
                st.code(e)

    if not todas:
        st.error("Nenhuma empresa encontrada. Tente outro CNAE, município ou estado.")
        st.stop()

    df = pd.DataFrame([formatar(e) for e in todas])
    df = df.drop_duplicates(subset=["CNPJ"])  # remove duplicatas entre CNAEs

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
                st.markdown(sugestao_abordagem(emp, nome_empresa, oferta_empresa, desc))
        else:
            st.warning("Não foi possível obter detalhes deste CNPJ agora.")

    # ── Exportar ──────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("📥 Exportar lista de prospects")
    col_dl1, col_dl2 = st.columns(2)

    csv = df_vis.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    col_dl1.download_button("⬇️ Baixar CSV",
        csv, f"zampasys_prospects_{nome_export}.csv", "text/csv",
        use_container_width=True)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df_vis.to_excel(w, index=False, sheet_name="Prospects")
    col_dl2.download_button("⬇️ Baixar Excel",
        buf.getvalue(), f"zampasys_prospects_{nome_export}.xlsx",
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
        st.markdown(sugestao_abordagem(emp, nome_empresa, oferta_empresa))

    st.divider()
    buf2 = io.BytesIO()
    pd.DataFrame([emp]).to_excel(buf2, index=False, sheet_name="CNPJ")
    st.download_button("⬇️ Baixar Excel", buf2.getvalue(),
        f"zampasys_cnpj_{cnpj_limpo}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# RESULTADO — GOOGLE MAPS
# ══════════════════════════════════════════════════════════════════════════════
elif aba == "🗺️ Google Maps" and btn_maps:

    if not maps_termo:
        st.error("Selecione uma categoria ou digite um termo de busca.")
        st.stop()

    if municipio_maps.strip() and not estado_maps:
        st.error("Selecione o estado ao informar uma cidade.")
        st.stop()
    cidade_exib = ", ".join(p for p in (municipio_maps.strip(), estado_maps) if p) or "Brasil"
    nome_maps_export = re.sub(r"[^\w-]+", "_", maps_termo).strip("_")[:30] or "busca"
    st.info(f"🗺️ Buscando **{maps_termo}** em **{cidade_exib}**")

    if maps_api_key.strip():
        # ── Busca via Places API ──────────────────────────────────────────────
        todas_maps: list = []
        proximo_token = None
        barra_m = st.progress(0, text="Consultando Google Maps API…")

        for i in range(1, paginas_maps + 1):
            barra_m.progress(i / paginas_maps, text=f"Página {i} de {paginas_maps}…")
            resultados, proximo_token = buscar_google_maps(
                maps_termo,
                municipio_maps.strip() or estado_maps,
                estado_maps,
                maps_api_key.strip(),
                proximo_token,
            )
            todas_maps.extend(resultados)
            if not proximo_token:
                break
            if i < paginas_maps:
                time.sleep(2)   # Places API exige ~2 s antes de usar next_page_token

        barra_m.empty()

        if not todas_maps:
            st.warning("Nenhum resultado encontrado. Verifique a API key e os termos de busca.")
        else:
            linhas = []
            for p in todas_maps:
                place_id = p.get("place_id", "")
                linhas.append({
                    "Nome":        p.get("name", ""),
                    "Endereço":    p.get("formatted_address", ""),
                    "Avaliação":   p.get("rating", ""),
                    "Avaliações":  p.get("user_ratings_total", ""),
                    "Status":      p.get("business_status", ""),
                    "Google Maps": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "",
                })
            df_maps = pd.DataFrame(linhas)

            c1, c2, c3 = st.columns(3)
            c1.metric("Total encontrado", len(df_maps))
            c2.metric("Com avaliação",    int((df_maps["Avaliação"] != "").sum()))
            c3.metric("Operando",         int((df_maps["Status"] == "OPERATIONAL").sum()))

            st.dataframe(
                df_maps,
                use_container_width=True,
                height=480,
                column_config={
                    "Google Maps": st.column_config.LinkColumn("Google Maps"),
                }
            )

            st.divider()
            csv_m = df_maps.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            buf_m = io.BytesIO()
            with pd.ExcelWriter(buf_m, engine="openpyxl") as w:
                df_maps.to_excel(w, index=False, sheet_name="GoogleMaps")
            col1, col2 = st.columns(2)
            col1.download_button("⬇️ Baixar CSV",
                csv_m, f"zampasys_maps_{nome_maps_export}.csv", "text/csv",
                use_container_width=True)
            col2.download_button("⬇️ Baixar Excel",
                buf_m.getvalue(), f"zampasys_maps_{nome_maps_export}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    else:
        # ── Sem API Key: gerar links de busca ─────────────────────────────────
        st.markdown("### 🔗 Links de Busca no Google Maps")
        st.markdown("Clique para abrir a busca diretamente no Google Maps:")
        st.divider()

        from urllib.parse import quote_plus

        local_cidade = ", ".join(
            p for p in (municipio_maps.strip(), estado_maps, "Brasil") if p
        )
        local_estado = ", ".join(p for p in (estado_maps, "Brasil") if p)
        url_cidade = (
            "https://www.google.com/maps/search/?api=1&query="
            + quote_plus(f"{maps_termo} em {local_cidade}")
        )
        url_estado = (
            "https://www.google.com/maps/search/?api=1&query="
            + quote_plus(f"{maps_termo} em {local_estado}")
        )

        col_a, col_b = st.columns(2)
        col_a.link_button(
            f"🗺️ {maps_termo.title()} em {municipio_maps.strip() or estado_maps or 'Brasil'}",
            url_cidade, use_container_width=True, type="primary"
        )
        if municipio_maps.strip():
            col_b.link_button(
                f"🗺️ {maps_termo.title()} em {estado_maps or 'todo o Brasil'}",
                url_estado, use_container_width=True
            )

        st.divider()
        st.info("💡 Para ver os resultados **dentro do app** com dados completos, "
                "insira uma **Google Maps Places API Key** na barra lateral.")
