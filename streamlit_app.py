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
st.markdown('<div class="section-title">🚨 Classificação do Evento (Diretrizes Oficiais)</div>', unsafe_allow_html=True)

tipo_ocorrencia = st.selectbox(
    "Selecione a natureza da ocorrência para aplicar o manual técnico:",
    [
        "Selecione uma opção...",
        "Acidente de Trânsito / Colisão / Choque / Abalroamento",
        "Falha Mecânica / Logística (Excesso de Jornada / Carga Tombada / Danos)",
        "Desvio de Segurança / Quebra de Regra de Ouro (Empilhadeiras / NR-11)",
        "Recolhimento em Revista (Notebooks / Celulares / Sem Documentação)",
        "Controle de Portaria (Instabilidade Ronda / Saída Fora do Horário / Trava Rodas)",
        "🔥 FATO NOVO / Ocorrência Complexa (Sem Modelo Prévio)"
    ]
)
st.markdown('</div>', unsafe_allow_html=True)

# Bloco do Relato Livre
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📝 Relato Técnico da Ocorrência</div>', unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; font-size:0.9rem;'>Dite ou escreva o relato bruto. Lembre-se: O BO deve ser reportado em até 1 hora após o fato.</p>", unsafe_allow_html=True)

relato_bruto = st.text_area("Descreva os fatos ocorridos no turno:", height=180, placeholder="Ex: No dia tal, às xx:xx, no Galpão X coluna xx, identificamos...")
st.markdown('</div>', unsafe_allow_html=True)

# Bloco de Anexos
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📸 Adicionar Evidências Visuais (Fotos do Contexto e Detalhes)</div>', unsafe_allow_html=True)
arquivo_anexado = st.file_uploader("Anexe evidências (Fotos amplas/fechadas, MVM, CNH, DANFE ou Croqui)", type=["png", "jpg", "jpeg"])

imagem_carregada = None
if arquivo_anexado is not None:
    try:
        imagem_carregada = Image.open(io.BytesIO(arquivo_anexado.read()))
        st.image(imagem_carregada, caption="📸 Imagem Anexada com Sucesso", use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar a imagem: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# 4. PROCESSAMENTO DOS PROMPTS ENRIQUECIDOS COM O MANUAL
if st.button("🚀 ENVIAR PARA PROCESSAMENTO"):
    if tipo_ocorrencia == "Selecione uma opção...":
        st.warning("Por favor, selecione a natureza da ocorrência antes de continuar.")
    elif relato_bruto.strip() == "":
        st.warning("Por favor, informe o relato da ocorrência antes de continuar.")
    else:
        
        # DEFINIÇÃO DO BANCO DE DIRETRIZES DA PÁGINA 3 E DO MANUAL
        diretrizes_conhecimento = """
        DIRETRIZES OBRIGATÓRIAS DO MANUAL (PÁGINA 3):
        1. Clareza e Objetividade: Texto estritamente técnico e factual. Sem opiniões pessoais ou termos subjetivos.
        2. Rastreabilidade de Terceiros: Para motoristas/prestadores externos, é OBRIGATÓRIO constar: RG/CPF, CNH com vencimento, telefone, endereço residencial e FILIAÇÃO COMPLETA (Pai e Mãe).
        3. Identificação de Lideranças: Exigir nome, sobrenome e registro do Líder, Supervisor ou Gerente da área responsável (Team Leaders não respondem administrativamente).
        4. Regra de Fotos: Devem ser registradas fotos amplas (para contexto) e fechadas (para foco no dano/placa/etiqueta).
        5. Prazo Operacional: O fato precisa ser reportado em até 1 hora no sistema.
        6. Protocolo de Acidentes/Incidentes: Todo evento com lesão ou acidente móvel exige conferir se houve acionamento do Técnico de Segurança do Trabalho, encaminhamento compulsório ao CSO, identificação da equipe médica que atendeu (médico/enfermeiro e CRM) e o desfecho clínico (retorno ao trabalho ou residência).
        7. Terminologia de Trânsito: Proibido usar o termo genérico 'danificado'. Use termos específicos: amassado, quebrado, riscado, trincado. Diferencie:
           - COLISÃO: Impacto geral entre corpos.
           - CHOQUE: Veículo em movimento contra obstáculo ou veículo parado.
           - ABALROAMENTO: Impacto lateral entre dois veículos em movimento.
        8. Casos de Revista/Notebooks: Rastrear marcas, patrimônios, etiquetas QR Code e conferir destinação à Alfândega.
        9. Casos de Logística/Carga: Conferir notas DANFE, códigos de desenho de peças, número de MVM e cumprimento da Lei 13.103 de limite de 5 horas de jornada física do motorista.
        """

        # --- FASE 1: O CLAUDE VALIDA BASEADO NAS REGRAS INJETADAS ---
        with st.spinner("🕵️ O Claude está auditando com base nas regras do Manual Técnico..."):
            prompt_auditoria = f"""
            Você é um auditor sênior de segurança patrimonial industrial da Stellantis.
            Sua missão é confrontar o relato do vigilante contra a nossa base de conhecimento oficial e apontar lacunas.

            BASE DE CONHECIMENTO TÉCNICA DO SISTEMA:
            {diretrizes_conhecimento}

            CATEGORIA DA OCORRÊNCIA SELECIONADA: {tipo_ocorrencia}
            RELATO DO TURNO: "{relato_bruto}"

            RESPONDA EXCLUSIVAMENTE em formato Markdown bem estruturado:
            1. **Status de Conformidade**: (COMPLETO se tiver tudo, ou INCOMPLETO se faltar dados).
            2. **Análise de Rastreabilidade**: (Liste o que foi identificado: locais/colunas, nomes, documentos, placas).
            3. **Lacunas Conforme Página 3**: (Aponte estritamente o que o vigilante esqueceu com base no manual, como falta de filiação, falta de dados de quem atendeu no CSO, uso do termo inadequado 'danificado', falta do registro do supervisor, ou estouro do prazo de 1 hora).
            """
            
            try:
                response_claude = anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt_auditoria}]
                )
                resultado_auditoria = response_claude.content[0].text
                st.markdown("### 📋 Auditoria de Conformidade (Claude 3.5 - Regras do Manual)")
                st.markdown(resultado_auditoria)
            except Exception as e:
                st.error(f"Erro na auditoria: {e}")
                resultado_auditoria = "Erro na auditoria."

        # --- FASE 2: O GEMINI FORMATA O BO PADRÃO DE EXCELÊNCIA ---
        with st.spinner("⚡ O Gemini está estruturando o Boletim de Ocorrência oficial..."):
            prompt_bo = f"""
            Você é um redator especialista em segurança corporativa industrial. Pegue o relato do vigilante e as considerações da auditoria e compile um Boletim de Ocorrência Interno oficial padrão Stellantis.
            Campos que não foram informados no texto bruto devem ficar marcados formalmente como "[NÃO INFORMADO]" para que fiquem evidentes.

            {diretrizes_conhecimento}

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
            - **Filiação Completa (Pai e Mãe)**: 
            - **Supervisor Direto da Parte (Nome, Registro e Contato)**: 

            **3. DADOS DE ATIVOS / VEÍCULOS / LOGÍSTICA**
            - **Equipamento/Veículo**: (Modelo, Marca, Prefixo ou Placas Combinadas de Carreta/Sider)
            - **Documentação de Carga/Material**: (MVM / DANFE / Patrimônio do Notebook / Termos de Liberação)
            - **Danos Materiais Especificados**: (Listagem detalhada usando os termos técnicos exatos: amassado, quebrado, riscado, trincado. Liste também avarias pré-existentes se houver)

            **4. DINÂMICA COMPLETA DOS FATOS & ALEGAÇÃO**
            - (Narrativa cronológica clara, impessoal e detalhada sobre o acontecimento).
            - **Alegação Coletada**: (Transcrição formal da justificativa apresentada pelo envolvido principal).

            **5. TRATATIVAS TÉCNICAS, ADMINISTRATIVAS & STATUS**
            - **Status Vigente do Caso**: (CONCLUÍDO NO LOCAL / EM ABERTO PARA INVESTIGAÇÃO)
            - **Resolução Operacional Imediata**: (Medidas tomadas pela equipe no local do fato, destinação de materiais à qualidade ou retenção)
            - **Suporte Médico / CSO**: (Dados de encaminhamento ao CSO, atendimento por enfermagem/médicos, CRM e desfecho clínico, se aplicável)
            - **Segurança do Trabalho (SESMT)**: (Envolvimento do Técnico de Segurança, Enquadramento em Regras de Ouro como a nº 8, Classificação da Gravidade ou Emissão de Notificação de Consequências)
            """
            
            try:
                model_gemini = genai.GenerativeModel("gemini-1.5-flash")
                response_gemini = model_gemini.generate_content(prompt_bo)
                
                st.markdown("---")
                st.markdown("### 📄 Documento Compilado (Gemini 1.5 Flash)")
                st.code(response_gemini.text, language="markdown")
                st.success("✨ Boletim técnico blindado e gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar o documento: {e}")
