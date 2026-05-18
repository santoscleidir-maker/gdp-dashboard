import streamlit as st
import google.generativeai as genai
import PIL.Image as PILImage
import io

# 1. CONFIGURAÇÃO DA PÁGINA E IDENTIDADE VISUAL
st.set_page_config(
    page_title="Sentinela Bravo - BO Eletrônico",
    page_icon="🛡️",
    layout="centered"
)

# Injeção de Meta Tags para transformar a página em Aplicativo de Celular
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

# Carrega o brasão oficial do Sentinela
try:
    logo_sentinela = PILImage.open("sentinela_icon_192.jpg")
    st.image(logo_sentinela, width=150)
except:
    pass

st.title("Sentinela Bravo")
st.markdown("<p class='subtitle'>Boletim de Ocorrência Eletrônico Inteligente • Planta Industrial</p>", unsafe_allow_html=True)

# 2. VALIDAÇÃO DE CHAVE DE API (Apenas Gemini agora)
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Erro: Certifique-se de configurar GEMINI_API_KEY nas Configurações do Streamlit.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model_gemini = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Erro ao inicializar o motor do sistema: {e}")
    st.stop()

# 3. INTERFACE DE SELEÇÃO E ENTRADA DE DADOS
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🚨 Natureza da Ocorrência Operacional</div>', unsafe_allow_html=True)

tipo_ocorrencia = st.selectbox(
    "Selecione a opção correspondente para a triagem:",
    [
        "🔥 GERAR BOLETIM UNIVERSAL (Qualquer Modelo do Manual)",
        "📦 Carga Tombada / Peças Molhadas / Danos em Racks",
        "❌ Recusa de Carga / Divergência Fiscal / Excesso de Jornada",
        "Acidente de Trânsito / Colisão Interna (Choque ou Abalroamento)",
        "Desvio de Segurança / Quebra de Regra de Ouro (Falta Grave)",
        "Controle de Acesso / Portaria (Notebooks / Instabilidade Ronda)"
    ]
)
st.markdown('</div>', unsafe_allow_html=True)

# Bloco do Relato Livre
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📝 Relato Técnico da Ocorrência</div>', unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; font-size:0.9rem;'>Escreva ou dite o relato bruto do seu turno. A IA vai enquadrar o texto no padrão oficial automaticamente.</p>", unsafe_allow_html=True)

relato_bruto = st.text_area("Descreva os fatos ocorridos no turno:", height=180, placeholder="Ex: Acionados pelo líder às xx:xx, informando sobre...")
st.markdown('</div>', unsafe_allow_html=True)

# Bloco de Anexos com Compactação Ativa
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📸 Adicionar Evidências Visuais (Compactação Ativa)</div>', unsafe_allow_html=True)
arquivo_anexado = st.file_uploader("Anexe evidências (Fotos, MVM, CNH, DANFE ou Croqui)", type=["png", "jpg", "jpeg"])

imagem_compactada = None
if arquivo_anexado is not None:
    try:
        dados_da_imagem = arquivo_anexado.read()
        img_original = PILImage.open(io.BytesIO(dados_da_imagem))
        
        if img_original.width > 1280:
            proporcao = 1280 / float(img_original.width)
            altura_alvo = int((float(img_original.height) * float(proporcao)))
            img_original = img_original.resize((1280, altura_alvo), resample=3) 
        
        buffer_ram = io.BytesIO()
        if img_original.mode in ("RGBA", "P"):
            img_original = img_original.convert("RGB")
            
        img_original.save(buffer_ram, format="JPEG", quality=75, optimize=True)
        buffer_ram.seek(0)
        
        imagem_compactada = PILImage.open(buffer_ram)
        st.image(imagem_compactada, caption="📸 Foto Otimizada com Sucesso (Memória Protegida)", use_container_width=True)
        
        if st.button("🗑️ Remover/Deletar Foto Atual"):
            st.rerun()
            
    except Exception as e:
        st.error(f"Erro ao otimizar imagem: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# 4. PROCESSAMENTO INTEGRADO E SEGURO (MÁXIMA ESTABILIDADE)
if st.button("🚀 ENVIAR PARA PROCESSAMENTO"):
    if relato_bruto.strip() == "":
        st.warning("Por favor, informe o relato da ocorrência antes de continuar.")
    else:
        
        # PROMPT COMPILADO DE AUDITORIA E FORMATAÇÃO (TUDO EM 1)
        prompt_unico = f"""
        Você é o assistente oficial de Inteligência Artificial do Squad Bravo, especializado em segurança patrimonial industrial da Stellantis.
        Sua missão é ler o relato bruto do vigilante, identificar qual é a natureza da ocorrência (dentre os mais de 10 modelos existentes no manual corporativo) e devolver duas seções claras.

        DIRETRIZES DA PÁGINA 3 DO MANUAL:
        - Linguagem puramente técnica, factual, impessoal e sem adjetivos subjetivos.
        - Exigência de rastreamento total: identificação de lideranças, dados completos de motoristas/colaboradores (CNH, RG, CPF, contato, endereço e filiação completa) e documentos de carga (DANFE/MVM).
        - Uso de termos exatos para avarias: amassado, riscado, quebrado, trincado.

        NATUREZA SELECIONADA OU IDENTIFICADA: {tipo_ocorrencia}
        RELATO DO VIGILANTE: "{relato_bruto}"

        RESPONDA EXCLUSIVAMENTE NO SEGUINTE FORMATO:

        ## 📋 AUDITORIA DE CONFORMIDADE (REGRAS DO MANUAL)
        - **Modelo de BO Identificado**: (Indique qual dos modelos do manual se aplica a este caso)
        - **Dados Críticos Localizados**: (Liste o que o vigilante informou de correto)
        - **Lacunas / O que falta coletar**: (Aponte quais dados cruciais da Página 3 ou do modelo específico ficaram faltando para fechar o caso com perfeição. Se estiver completo, elogie o preenchimento)

        ---

        ## 📄 BOLETIM DE OCORRÊNCIA INTERNO ESTRUTURADO

        ### 🛡️ SQUAD BRAVO - RELATÓRIO OPERACIONAL

        **1. DADOS DE CONTROLE & ACIONAMENTO**
        - **Data/Hora do Fato**: [Extrair do texto ou marcar como NÃO INFORMADO]
        - **Localização Exata**: (Galpão, Coluna específica, Prédio, Sentido da Via ou Portaria)
        - **Líder/Supervisor Solicitante & Registro**: 
        - **Horário do Chamado**: 
        - **Vigilante Relator / Registro**: 

        **2. QUALIFICAÇÃO CRUZADA DOS ENVOLVIDOS (RASTREAMENTO PÁG 3)**
        - **Vínculo**: (Colaborador Interno / Terceiro / Prestador / Fornecedor)
        - **Nome Completo**: 
        - **Matrícula / Registro Funcional**: 
        - **Empresa / Transportadora / Fornecedor**: 
        - **Documentos (RG/CPF)**: 
        - **Habilitação (CNH / Vencimento)**: 
        - **Telefone de Contato**: 
        - **Endereço Residencial**: 
        - **Filiação Completa (Nome do Pai e da Mãe)**: 
        - **Supervisor Direto da Parte (Nome, Registro e Contato)**: 

        **3. DADOS DE ATIVOS / VEÍCULOS / LOGÍSTICA**
        - **Equipamento/Veículo**: (Modelo, Marca, Prefixo de Empilhadeira, Placas de Carreta ou identificação de Notebook/Objetos)
        - **Documentação de Carga/Material**: (MVM / DANFE / Termo de Responsabilidade / Código de Desenho da Peça)
        - **Danos Materiais Especificados**: (Listagem detalhada das avarias encontradas: amassado, quebrado, riscado, trincado. Se não houver, citar 'Sem avarias')

        **4. DINÂMICA COMPLETA DOS FATOS & ALEGAÇÃO**
        - (Narrativa cronológica detalhada, impessoal e clara dos fatos baseada no relato bruto).
        - **Alegação Coletada**: (Transcrição formal da justificativa apresentada pelo envolvido principal).

        **5. TRATATIVAS TÉCNICAS, ADMINISTRATIVAS & STATUS**
        - **Status Vigente do Caso**: (CONCLUÍDO NO LOCAL / EM ABERTO PARA INVESTIGAÇÃO)
        - **Resolução Operacional Imediata**: (Medidas tomadas pela equipe: destinação de materiais, acionamento de manutenção, liberação com crachá manual, etc.)
        - **Segurança do Trabalho / Suporte Técnico**: (Registro se houve acompanhamento do SESMT, CSO ou supervisão da área, conforme aplicável para a natureza do fato)
        """
        
        with st.spinner("⚡ O Gemini está analisando as regras e estruturando o seu documento oficial..."):
            try:
                response = model_gemini.generate_content(prompt_unico)
                st.markdown(response.text)
                st.success("✨ Processamento concluído com sucesso e sem erros!")
            except Exception as e:
                st.error(f"Erro ao processar o relatório: {e}")
