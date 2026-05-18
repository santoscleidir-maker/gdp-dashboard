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
st.markdown('<div class="section-title">🚨 Classificação do Evento</div>', unsafe_allow_html=True)

tipo_ocorrencia = st.selectbox(
    "Selecione a natureza da ocorrência para direcionar a conferência técnica:",
    [
        "Selecione uma opção...",
        "Acidente de Trânsito / Colisão (Vias Internas / Alças / Rotatórias)",
        "Falha Mecânica / Logística de Carga (Avaria de Carga / Válvulas / Pátios)",
        "Desvio de Segurança / Quebra de Regra de Ouro (Veículos Móveis / Empilhadeiras)",
        "Avaria / Danos ao Patrimônio (Qualidade / Reparo / MSO / Portarias)",
        "🔥 FATO NOVO / Ocorrência Complexa (Sem Modelo Prévio)"
    ]
)
st.markdown('</div>', unsafe_allow_html=True)

# Bloco do Relato Livre
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📝 Relato Técnico da Ocorrência</div>', unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; font-size:0.9rem;'>Dite ou escreva focando na localização exata (Galpão, Coluna, Via/Sentido), prefixos de equipamentos, registros/matrículas, alegações e encaminhamentos médicos (CSO).</p>", unsafe_allow_html=True)

relato_bruto = st.text_area("Descreva os fatos ocorridos no turno:", height=180, placeholder="Ex: No dia tal, às xx:xx, no Galpão X coluna xx, identificamos...")
st.markdown('</div>', unsafe_allow_html=True)

# Bloco de Anexos
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📸 Adicionar Fotos, Documentos ou Desenho da Peça</div>', unsafe_allow_html=True)
arquivo_anexado = st.file_uploader("Toque para abrir a câmera ou anexar evidências (Fotos, MVM, CNH, Croqui)", type=["png", "jpg", "jpeg"])

imagem_carregada = None
if arquivo_anexado is not None:
    try:
        imagem_carregada = Image.open(io.BytesIO(arquivo_anexado.read()))
        st.image(imagem_carregada, caption="📸 Imagem Anexada com Sucesso", use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar a imagem: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# 4. PROCESSAMENTO DOS PROMPTS DINÂMICOS
if st.button("🚀 ENVIAR PARA PROCESSAMENTO"):
    if tipo_ocorrencia == "Selecione uma opção...":
        st.warning("Por favor, selecione a natureza da ocorrência antes de continuar.")
    elif relato_bruto.strip() == "":
        st.warning("Por favor, informe o relato da ocorrência antes de continuar.")
    else:
        # Criação do Checklist Rigoroso baseado nos novos exemplos reais
        checklist_especifico = """
        - LOCALIZAÇÃO MICROMÉTRICA: Especificar detalhadamente o ponto exato da planta (Ex: Galpão XX e número das Colunas correspondentes, Alça de acesso, Km, Sentido da Via interna ou Portaria de controle).
        - RASTREABILIDADE TOTAL: Nome completo dos envolvidos, cruzamento de dados (Vínculo: Interno/Terceiro), matrículas, registros funcionais, telefones, RG/CPF, CNH com vencimento, endereço residencial e filiação completa (Pai e Mãe).
        - DADOS DOS EQUIPAMENTOS/CARGA: Placas combinadas (Cavalete e Carreta/Sider), fornecedor, transportadora, número do documento fiscal ou MVM, prefixo e modelo de empilhadeiras ou frotas internas.
        - LIDERANÇAS E ACIONAMENTOS: Nomes e registros das lideranças cientes de AMBAS AS PARTES envolvidas, identificação de quem solicitou o apoio da segurança patrimonial e a hora exata do chamado.
        - ALEGAÇÃO CRUCIAL: Registro textual e detalhado da alegação apresentada pelo motorista ou funcionário envolvido.
        - DANOS MATERIAIS ESPECÍFICOS: Listagem minuciosa dos danos, avarias pré-existentes, peças faltantes ou necessidade de desenho técnico da peça.
        - ENCAMINHAMENTO E STATUS TÉCNICO: O caso segue em aberto ou foi concluído? Houve acionamento/atendimento médico no CSO (mencionar nomes da equipe de enfermagem ou médicos e CRM)? Houve autoria técnica da Segurança do Trabalho (SESMT), emissão de Notificação de Consequências ou classificação da gravidade (Ex: Falta Grave)?
        """

        # --- FASE 1: O CLAUDE VALIDA O CHECKLIST ---
        with st.spinner("🕵️ O Claude está auditando os dados do relato..."):
            prompt_auditoria = f"""
            Você é um auditor sênior de segurança patrimonial e compliance industrial focado em plantas automotivas complexas.
            Analise se o relato bruto do vigilante preenche rigidamente todos os requisitos necessários de amarração técnica e rastreabilidade conforme nossos padrões operacionais.

            CATEGORIA SELECIONADA: {tipo_ocorrencia}
            CHECKLIST DE CONFERÊNCIA EXIGIDO:
            {checklist_especifico}

            RELATO COLETADO:
            "{relato_bruto}"

            RESPONDA EXCLUSIVAMENTE em formato Markdown bem estruturado:
            1. **Status de Conformidade**: (COMPLETO ou INCOMPLETO).
            2. **Dados Críticos Encontrados**: (Destaque Local exato/Colunas, Envolvidos, Líderes e Horários identificados).
            3. **Lacunas Operacionais**: (Indique com clareza amigável e direta quais dados fundamentais faltaram no relato, como: 'Faltou indicar a coluna do galpão', 'Faltou o registro do líder', 'Não consta se o envolvido foi direcionado ao CSO', etc).
            """
            
            try:
                response_claude = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt_auditoria}]
                )
                resultado_auditoria = response_claude.content[0].text
                st.markdown("### 📋 Análise de Dados (Claude 3.5 Sonnet)")
                st.markdown(resultado_auditoria)
            except Exception as e:
                st.error(f"Erro ao processar auditoria com o Claude: {e}")
                resultado_auditoria = "Erro na auditoria."

        # --- FASE 2: O GEMINI GERA O BO PADRÃO DE EXCELÊNCIA ---
        with st.spinner("⚡ O Gemini está padronizando o Boletim de Ocorrência oficial..."):
            prompt_bo = f"""
            Você é um redator especialista em segurança corporativa de alta performance. Pegue o relato do vigilante e as considerações da auditoria e compile um Boletim de Ocorrência Interno oficial, extremamente técnico, impessoal, sem erros gramaticais e perfeitamente estruturado.
            Campos não mencionados no texto bruto devem ser identificados formalmente como "[NÃO INFORMADO]" para preenchimento posterior.

            RELATO DO VIGILANTE: "{relato_bruto}"

            ESTRUTURE O DOCUMENTO EXATAMENTE NESTES TÓPICOS:
            ### 🛡️ BOLETIM DE OCORRÊNCIA INTERNO - SQUAD BRAVO

            **1. DADOS DE CONTROLE & ACIONAMENTO**
            - **Data/Hora do Evento**: 
            - **Localização Exata**: (Indicar Galpão, Coluna, Bloco, Sentido da Via ou Alça de Acesso Interna)
            - **Líder Solicitante & Registro**: 
            - **Horário do Acionamento da Segurança**: 
            - **Vigilante Relator / Registro**: 

            **2. QUALIFICAÇÃO CRUZADA DOS ENVOLVIDOS**
            *(Replique este bloco se houver mais de um condutor, colaborador ou operador)*
            - **Vínculo**: (Colaborador Interno / Terceiro / Prestador / Fornecedor)
            - **Nome Completo**: 
            - **Matrícula / Registro Funcional**: 
            - **Empresa / Transportadora / Fornecedor**: 
            - **Documentos (RG/CPF)**: 
            - **Habilitação (CNH / Vencimento)**: 
            - **Telefone de Contato**: 
            - **Endereço Residencial**: 
            - **Filiação Completa**: 
            - **Liderança Direta da Parte (Nome, Registro e Contato)**: 

            **3. DADOS DE ATIVOS / VEÍCULOS / LOGÍSTICA**
            - **Equipamento/Veículo**: (Modelo, Marca, Prefixo ou Placas Combinadas de Carreta/Sider)
            - **Documentação de Carga**: (MVM / Manifesto de Resíduos / Nota Fiscal)
            - **Danos Materiais Especificados**: (Listagem detalhada das avarias encontradas ou avarias pré-existentes identificadas na inspeção)
            - **Peças Faltantes ou Avariadas**: 

            **4. DINÂMICA COMPLETA DOS FATOS & ALEGAÇÃO**
            - (Narrativa cronológica clara, impessoal e detalhada sobre o acontecimento).
            - **Alegação Coletada**: (Transcrição ou síntese formal da alegação de defesa ou justificativa apresentada pelo envolvido principal).

            **5. TRATATIVAS TÉCNICAS, ADMINISTRATIVAS & STATUS**
            - **Status Vigente do Caso**: (CONCLUÍDO NO LOCAL / EM ABERTO PARA INVESTIGAÇÃO)
            - **Resolução Operacional Imediata**: (Medidas tomadas pela equipe no local do fato)
            - **Suporte Médico / CSO**: (Dados de encaminhamento ao CSO, atendimento por enfermagem/médicos e CRM, se aplicável)
            - **Segurança do Trabalho (SESMT)**: (Envolvimento da Segurança do Trabalho, Enquadramento em Regras de Ouro, Classificação da Gravidade como Falta Grave/Média/Leve ou Emissão de Notificação de Consequências com dados do emissor)
            """
            
            try:
                model_gemini = genai.GenerativeModel("gemini-1.5-flash")
                response_gemini = model_gemini.generate_content(prompt_bo)
                
                st.markdown("---")
                st.markdown("### 📄 Documento Compilado (Gemini 1.5 Flash)")
                st.code(response_gemini.text, language="markdown")
                st.success("✨ Boletim técnico gerado com sucesso! Pronto para ser extraído e enviado para a gerência.")
            except Exception as e:
                st.error(f"Erro ao gerar o documento com o Gemini: {e}")
