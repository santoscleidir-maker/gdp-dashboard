import streamlit as st
import google.generativeai as genai
from anthropic import Anthropic
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

# 4. PROCESSAMENTO DOS PROMPTS ENRIQUECIDOS COM O MANUAL
if st.button("🚀 ENVIAR PARA PROCESSAMENTO"):
    if tipo_ocorrencia == "Selecione uma opção...":
        st.warning("Por favor, selecione a natureza da ocorrência antes de continuar.")
    elif relato_bruto.strip() == "":
        st.warning("Por favor, informe o relato da ocorrência antes de continuar.")
    else:
        
        # DEFINIÇÃO DO CHECKLIST DINÂMICO
        checklist_dinamico = ""
        if "Carga Tombada" in tipo_ocorrencia:
            checklist_dinamico = """
            - Local exato: Identificação obrigatória do Galpão e número das Colunas.
            - Equipamento: Prefixo e modelo da empilhadeira Hyster envolvida, nome, matrícula e setor do operador.
            - Material: Quantidade exata de peças, nome do material, número do desenho industrial e número da DANFE/Nota Fiscal.
            - Acionamento: Nome do Supervisor/Líder e matrícula da área, e nome/matrícula da Técnica de Segurança do Trabalho que avaliou.
            - Saúde: Registro se houve ou não necessidade de encaminhar o operador ao CSO (Centro de Saúde Ocupacional).
            - Destinação: Para qual galpão/setor da Qualidade as peças avariadas foram direcionadas.
            """
        elif "Recusa de Carga" in tipo_ocorrencia:
            checklist_dinamico = """
            - Documentação: Número da Nota Fiscal (DANFE), número do MVM (Manifesto), nome do Fornecedor e da Transportadora.
            - Identificação do Motorista: Nome completo, RG/CPF, CNH com validade, telefone de contato, endereço residencial e filiação completa (Pai e Mãe).
            - Motivo Comercial/Fiscal: Descrição exata do porquê a carga foi recusada (Avaria, erro de nota, peças molhadas) ou se estourou a Lei 13.103 de excesso de jornada (limite de 5h).
            - Responsáveis: Nome do conferente da logística que recusou e hora exata do travamento na portaria.
            """
        elif "Acidente de Trânsito" in tipo_ocorrencia:
            checklist_dinamico = """
            - Terminologia Correta: Não usar a palavra 'danificado'. Diferenciar se foi COLISÃO (geral), CHOQUE (veículo contra obstáculo/parado) ou ABALROAMENTO (lateral entre dois em movimento).
            - Veículos: Placas combinadas (Cavalete e Carreta/Sider), marcas, modelos e prefixos.
            - Qualificação: Dados completos dos condutores (Interno ou Terceiro, CNH, telefones, endereço e filiação).
            - Atendimento: Se acionou ambulância (placa), remoção, atendimento no CSO, nome do enfermeiro/médico e CRM com desfecho clínico.
            """
        elif "Desvio de Segurança" in tipo_ocorrencia:
            checklist_dinamico = """
            - Enquadramento: Qual Regra de Ouro foi violada (Ex: Regra nº 8)? 
            - Infracção: Descrição clara e impessoal do ato operacional/falha (Ex: transportar rack de frente tirando visibilidade, falta de EPI).
            - Punição Técnica: Classificação do SESMT (Falta Leve, Média ou Grave) e número da Emissão de Notificação de Consequências de Saúde e Segurança com hora exata e nome do emissor.
            """
        else:
            checklist_dinamico = """
            - Princípio do Rastreamento Absoluto (Página 3): Dados pessoais completos (CNH, contatos, endereço residencial, filiação completa).
            - Lideranças: Identificação de supervisores/gerentes de ambas as partes envolvidas (com registro).
            - Status do Caso: Se o caso foi resolvido na hora ou SEGUE EM ABERTO. Menção se a Segurança do Trabalho acompanhou as tratativas.
            """

        diretrizes_gerais = "DIRETRIZES DA PÁGINA 3: Texto puramente técnico, impessoal e factual. Sem opiniões ou adjetivos subjetivos. Prazo de lançamento limite de até 1 hora após o fato. Uso de terminologia detalhada para avarias (amassado, riscado, quebrado, trincado). Team Leaders não respondem administrativamente, exigir Supervisor ou Gerente."

        # --- FASE 1: O CLAUDE AUDITA O RELATO ---
        with st.spinner("🕵️ O Claude está auditando o relato..."):
            prompt_auditoria = f"""
            Você é um auditor sênior de segurança patrimonial industrial da Stellantis.
            Sua missão é confrontar o relato bruto fornecido contra o manual técnico específico e as regras da Página 3.

            REGRAS ESPECÍFICAS DA NATUREZA SELECIONADA:
            {checklist_dinamico}

            DIRETRIZES GERAIS:
            {diretrizes_gerais}

            RELATO DO TURNO ENVIADO:
            "{relato_bruto}"

            RESPONDA EXCLUSIVAMENTE em formato Markdown bem estruturado:
            1. **Status de Conformidade**: (COMPLETO ou INCOMPLETO).
            2. **Dados Críticos Identificados**: (Liste de forma resumida o que foi localizado).
            3. **Lacunas Operacionais**: (Indique diretamente o que o vigilante esqueceu de preencher).
            """
            
            try:
                # CORREÇÃO: Utilizando a nomenclatura de modelo atualizada e definitiva da Anthropic
                response_claude = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-latest",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt_auditoria}]
                )
                st.markdown("### 📋 Auditoria de Conformidade (Claude 3.5 - Regras do Manual)")
                st.markdown(response_claude.content[0].text)
            except Exception as e:
                st.error(f"Erro na auditoria do Claude: {e}")

        # --- FASE 2: O GEMINI GERA O DOCUMENTO FINAL ---
        with st.spinner("⚡ O Gemini está estruturando o Boletim de Ocorrência oficial..."):
            prompt_bo = f"""
            Você é um redator sênior especializado em relatórios corporativos de segurança industrial. 
            Pegue o relato do vigilante e estruture um Boletim de Ocorrência Interno oficial padrão Stellantis.
            Campos obrigatórios não informados devem ficar marcados formalmente como "[NÃO INFORMADO]".

            NATUREZA: {tipo_ocorrencia}
            RELATO DO VIGILANTE: "{relato_bruto}"

            ESTRUTURE O DOCUMENTO EXATAMENTE NESTES TÓPICOS:
            ### 🛡️ BOLETIM DE OCORRÊNCIA INTERNO - SQUAD BRAVO

            **1. DADOS DE CONTROLE & ACIONAMENTO**
            - **Data/Hora do Fato**: 
            - **Localização Exata**: (Indicar Galpão, Coluna específica, Prédio, Sentido da Via ou Portaria)
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
            - **Equipamento/Veículo**: (Modelo, Marca, Prefixo de Empilhadeira ou Placas Combinadas de Carreta/Sider)
            - **Documentação de Carga/Material**: (MVM / DANFE / Código de Desenho da Peça)
            - **Danos Materiais Especificados**: (Listagem detalhada das avarias encontradas: amassado, quebrado, riscado, trincado)

            **4. DINÂMICA COMPLETA DOS FATOS & ALEGAÇÃO**
            - (Narrativa cronológica detalhada, impessoal e clara dos fatos).
            - **Alegação Coletada**: (Transcrição formal da justificativa apresentada pelo envolvido principal).

            **5. TRATATIVAS TÉCNICAS, ADMINISTRATIVAS & STATUS**
            - **Status Vigente do Caso**: (CONCLUÍDO NO LOCAL / EM ABERTO PARA INVESTIGAÇÃO)
            - **Resolução Operacional Imediata**: (Medidas tomadas pela equipe: destinação de materiais à qualidade, acionamento de manutenção, etc.)
            - **Suporte Médico / CSO**: (Dados de encaminhamento ao CSO, atendimento por enfermeiro/médico, CRM e desfecho clínico, se aplicável)
            - **Segurança do Trabalho (SESMT)**: (Envolvimento do Técnico de Segurança, enquadramento em Regras de Ouro, gravidade do desvio e dados da Notificação de Consequências se emitida)
            """
            
            try:
                model_gemini = genai.GenerativeModel("gemini-1.5-flash")
                response_gemini = model_gemini.generate_content(prompt_bo)
                
                st.markdown("---")
                st.markdown("### 📄 Documento Compilado (Gemini 1.5 Flash)")
                st.code(response_gemini.text, language="markdown")
                st.success("✨ Boletim técnico pronto! Nenhuma imagem foi guardada no celular, mantendo a memória limpa.")
            except Exception as e:
                st.error(f"Erro ao gerar o documento: {e}")
