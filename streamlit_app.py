import streamlit as st
import google.generativeai as genai
from anthropic import Anthropic
from PIL import Image
import io

# 1. CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL
st.set_page_config(
    page_title="Sentinela Bravo - BO Eletrônico",
    page_icon="🛡️",
    layout="centered"
)

# Injeção de Meta Tags para transformar a página em Aplicativo de Celular (Ícone na Tela Inicial)
st.markdown("""
    <head>
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Sentinela Bravo">
        <meta name="mobile-web-app-capable" content="yes">
        
        <link rel="apple-touch-icon" href="sentinela_icon_192.jpg">
        <link rel="icon" sizes="192x192" href="sentinela_icon_192.jpg">
    </head>
""", unsafe_allow_html=True)

# Estilização profissional em modo escuro padrão Stellantis
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    h1 { color: #f97316; text-align: center; margin-bottom: 0px; }
    .subtitle { color: #8b949e; text-align: center; font-size: 1.1rem; margin-bottom: 2rem; }
    .section-card {
        background-color: #161b22;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #30363d;
        margin-bottom: 15px;
    }
    .section-title {
        color: #f97316;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Carrega o brasão oficial do Sentinela no topo da página
try:
    logo_sentinela = Image.open("sentinela_icon_192.jpg")
    st.image(logo_sentinela, width=150)
except:
    pass

st.title("Sentinela Bravo")
st.markdown("<p class='subtitle'>Boletim de Ocorrência Eletrônico Inteligente • Planta Industrial</p>", unsafe_allow_html=True)

# 2. VALIDAÇÃO DE CHAVES DE API
if "GEMINI_API_KEY" not in st.secrets or "CLAUDE_API_KEY" not in st.secrets:
    st.error("Erro: Certifique-se de configurar GEMINI_API_KEY e CLAUDE_API_KEY nas Configurações do Streamlit.")
    st.stop()

# Inicialização das APIs
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    anthropic_client = Anthropic(api_key=st.secrets["CLAUDE_API_KEY"])
except Exception as e:
    st.error(f"Erro ao inicializar as APIs: {e}")
    st.stop()

# 3. INTERFACE DE SELEÇÃO E ENTRADA DE DADOS
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🚨 Natureza da Ocorrência Operacional</div>', unsafe_allow_html=True)

tipo_ocorrencia = st.selectbox(
    "Selecione a opção correspondente para carregar as regras de auditoria:",
    [
        "Selecione uma opção...",
        "Acidente de Trânsito / Colisão Interna (Choque ou Abalroamento)",
        "📦 Carga Tombada / Peças Molhadas / Danos em Racks",
        "❌ Recusa de Carga / Divergência Fiscal / Excesso de Jornada",
        "Desvio de Segurança / Quebra de Regra de Ouro (Falta Grave)",
        "Controle de Acesso / Portaria (Notebooks / Instabilidade Ronda)",
        "🔥 FATO NOVO / Ocorrência Complexa (Sem Modelo Prévio)"
    ]
)
st.markdown('</div>', unsafe_allow_html=True)

# Bloco do Relato Livre
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📝 Relato Técnico da Ocorrência</div>', unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; font-size:0.9rem;'>Dite ou escreva o relato bruto. Foque na localização micrométrica (Galpão, Coluna), dados de motoristas/líderes e documentos (DANFE/MVM).</p>", unsafe_allow_html=True)

relato_bruto = st.text_area("Descreva os fatos ocorridos no turno:", height=180, placeholder="Ex: Acionados pelo líder às xx:xx, no Galpão 04 coluna 26AB...")
st.markdown('</div>', unsafe_allow_html=True)

# Bloco de Anexos com Compactação Automática em tempo de execução
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📸 Adicionar Evidências Visuais (Compactação Ativa)</div>', unsafe_allow_html=True)
arquivo_anexado = st.file_uploader("Anexe evidências (Fotos, MVM, CNH, DANFE ou Croqui)", type=["png", "jpg", "jpeg"])

imagem_compactada = None
if arquivo_anexado is not None:
    try:
        img_original = Image.open(arquivo_anexado)
        
        if img_original.width > 1280:
            proporcao = 1280 / float(img_original.width)
            altura_alvo = int((float(img_original.height) * float(proporcao)))
            img_original = img_original.resize((1280, altura_alvo), Image.Resampling.LANCZOS)
        
        buffer_ram = io.BytesIO()
        if img_original.mode in ("RGBA", "P"):
            img_original = img_original.convert("RGB")
        img_original.save(buffer_ram, format="JPEG", quality=75, optimize=True)
        buffer_ram.seek(0)
