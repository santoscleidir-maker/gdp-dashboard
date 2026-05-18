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

# Estilização para manter a interface profissional e escura
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

# Carrega o brasão oficial da Equipe Bravo
try:
    logo_sentinela = Image.open("sentinela_icon_192.jpg")
    st.image(logo_sentinela, width=150)
except:
    pass

st.title("Sentinela Bravo")
st.markdown("<p class='subtitle'>Boletim de Ocorrência Eletrônico Inteligente • Padrão Stellantis</p>", unsafe_allow_html=True)

# 2. VALIDAÇÃO DE CHAVES DE API
if "GEMINI_API_KEY" not in st.secrets or "CLAUDE_API_KEY" not in st.secrets:
    st.error("Erro: Certifique-se de configurar GEMINI_API_KEY e CLAUDE_API_KEY nas Configurações do Streamlit.")
    st.stop()

# Inicialização dos clientes das APIs
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
    "Selecione a natureza da ocorrência para direcionar o checklist:",
    [
        "Selecione uma opção...",
        "Acidente de Trânsito / Colisão Logística (Danos/Carga)",
        "Avaria / Danos ao Patrimônio / Qualidade / Reparo / MSO / Near Miss",
        "Furto / Roubo / Extravio / Peças Faltantes",
        "Anormalidade / Atitude Suspeita / Acidentes com Funcionários ou Objetos"
    ]
)
st.markdown('</div>', unsafe_allow_html=True)

# Bloco do Relato Livre (Vigilante dita ou escreve)
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📝 Relato da Ocorrência</div>', unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; font-size:0.9rem;'>Pode ditar ou escrever do seu jeito! Inclua nomes, horários, placas, alegações e o que foi feito.</p>", unsafe_allow_html=True)

relato_bruto = st.text_area("O que aconteceu no turno?", height=150, placeholder="Ex: Acionados pelo líder fulano às 08h... motorista terceiro alega que...")
st.markdown('</div>', unsafe_allow_html=True)

# Bloco de Anexos (Fotos da ocorrência, documentos, croquis, peças avariadas)
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📸 Adicionar Fotos, Documentos ou Desenho da Peça</div>', unsafe_allow_html=True)
arquivo_anexado = st.file_uploader("Toque para abrir a câmera ou anexar um arquivo/croqui", type=["png", "jpg", "jpeg"])

imagem_carregada = None
if arquivo_anexado is not None:
    try:
        imagem_carregada = Image.open(io.BytesIO(arquivo_anexado.read()))
        st.image(imagem_carregada, caption="📸 Imagem Anexada com Sucesso", use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao carregar a imagem: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# 4. PROCESSAMENTO E CRIAÇÃO DOS PROMPTS DINÂMICOS
if st.button("🚀 ENVIAR PARA PROCESSAMENTO"):
    if tipo_ocorrencia == "Selecione uma opção...":
        st.warning("Por favor, selecione a natureza da ocorrência antes de processar.")
    elif relato_bruto.strip() == "":
        st.warning("Por favor, digite ou dite o relato da ocorrência antes de processar.")
    else:
        # Montagem do checklist dinâmico com base na seleção do usuário
        checklist_especifico = ""
        if "Acidente de Trânsito" in tipo_ocorrencia:
            checklist_especifico = """
            - Identificação dos envolvidos: Se é funcionário Stellantis ou terceiro.
            - Dados do condutor: Nome completo, CNH, telefone, endereço de residência e filiação (Pai/Mãe).
            - Dados do veículo: Placa, prefixo, MVM, modelo e o desenho/descrição exata da peça avariada.
            - Líderes: Nome do líder do setor e telefone, líder solicitante da ocorrência e hora exata da solicitação.
            - Dinâmica: Houve batida? Houve danos na carga? Quem é o setor responsável (Qualidade, Reparo, MSO)?
            - Alegação: Qual é a alegação do motorista/terceiro?
            - Vigilante Relator e Solução: Quem está relatando e qual foi a solução/desfecho dado no local?
            """
        elif "Avaria / Danos ao Patrimônio" in tipo_ocorrencia:
            checklist_especifico = """
            - Natureza: É Qualidade, Reparo, MSO ou Near Miss (Quase Acidente)?
            - Identificação: Envolveu funcionários Stellantis ou terceiros? (Nome, ID, empresa, telefone).
            - Líderes: Quem solicitou o apoio da segurança, que horas solicitou, e quem é o líder responsável pelo setor.
            - Descrição física: O que foi danificado, quais peças estão avariadas ou faltantes.
            - Solução e Vigilante Relator: Medidas tomadas para conter o risco e identificação do relator.
            """
        elif "Furto / Roubo" in tipo_ocorrencia:
            checklist_especifico = """
            - Itens: Quais peças estão avariadas ou faltantes? (Descrição detalhada ou desenho da peça se aplicável).
            - Dados do suspeito/envolvido: Se terceiro ou funcionário, telefone, CNH, endereço, filiação.
            - Documentação: MVM (se aplicável), nota fiscal ou documento do material.
            - Solicitação: Quem deu falta, que horas o vigilante foi acionado e quem é o líder solicitante.
            - Desfecho: Qual foi a solução ou encaminhamento.
            """
        else:
            checklist_especifico = """
            - Envolvidos: Funcionário Stellantis ou terceiros (Telefone, CNH, endereço, filiação).
            - Acidentes: Envolveu pessoas ou objetos/equipamentos? Houve Near Miss?
            - Atendimento: Quem solicitou a presença da segurança e a hora exata. Líder do setor e contato.
            - Providências: Qual foi a solução imediata e quem é o vigilante relator.
            """

        # --- FASE 1: O CLAUDE VALIDA O CHECKLIST ---
        with st.spinner("🕵️ O Claude está auditando os dados do relato..."):
            prompt_auditoria = f"""
            Você é um auditor rigoroso de segurança patrimonial industrial da planta Stellantis.
            Sua missão é analisar se o relato bruto do vigilante preenche TODOS os requisitos do checklist exigido para esta categoria.

            CATEGORIA DA OCORRÊNCIA: {tipo_ocorrencia}

            CHECKLIST EXIGIDO QUE DEVE SER CONFERIDO:
            {checklist_especifico}

            RELATO DO VIGILANTE:
            "{relato_bruto}"

            RESPOSDA EXCLUSIVAMENTE em formato Markdown bem estruturado:
            1. **Status de Conformidade**: (Diga se o relato está "COMPLETO" ou "INCOMPLETO" para gerar um BO oficial).
            2. **Dados Encontrados**: (Liste de forma resumida o que ele informou).
            3. **Lacunas/Dados Faltantes**: (Aponte CLARAMENTE o que faltou informar de forma direta e amigável, ex: 'Faltou informar a CNH e a filiação do motorista terceiro').
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

        # --- FASE 2: O GEMINI GERA O COMPILADO DO BO PADRÃO STELLANTIS ---
        with st.spinner("⚡ O Gemini está estruturando o Boletim de Ocorrência oficial..."):
            prompt_bo = f"""
            Você é um redator sênior de segurança corporativa especializado em relatórios industriais padrão Stellantis.
            Pegue o relato bruto fornecido pelo vigilante, as validações feitas pelo auditor, e estruture um Boletim de Ocorrência Eletrônico limpo, formal, sem erros de digitação e extremamente profissional.

            Caso faltem dados (como filiação, CNH, líder solicitante), deixe o campo indicado como "[NÃO INFORMADO]" para que possa ser preenchido manualmente depois.

            CATEGORIA: {tipo_ocorrencia}
            RELATO DO VIGILANTE: "{relato_bruto}"

            ESTRUTURE O BO EXATAMENTE NESTES TÓPICOS:
            ### 🛡️ BOLETIM DE OCORRÊNCIA ELETRÔNICO - EQUIPE BRAVO

            **1. DADOS GERAIS DO ACIONAMENTO**
            - **Líder Solicitante**: 
            - **Horário da Solicitação**: 
            - **Vigilante Relator**: 
            - **Setor Responsável/Área**: (Qualidade / Reparo / MSO / Logística)

            **2. QUALIFICAÇÃO DOS ENVOLVIDOS**
            - **Vínculo**: (Funcionário Stellantis / Terceiro)
            - **Nome Completo**: 
            - **CNH / Documento**: 
            - **Telefone de Contato**: 
            - **Endereço de Residência**: 
            - **Filiação**: 
            - **Líder Direto do Envolvido & Tel**: 

            **3. DETALHES DOS MATERIAIS / VEÍCULOS**
            - **Placa/Prefixo**: 
            - **MVM / Documentação de Carga**: 
            - **Danos na Carga / Batidas**: (Sim / Não - Detalhar se houve)
            - **Peças Avariadas ou Faltantes**: (Descreva as peças e mencione se há desenho/anexo da peça)

            **4. DINÂMICA DOS FATOS & ALEGAÇÃO**
            - (Formatar o relato cronológico dos fatos, de forma clara e impessoal, incluindo textualmente a ALEGAÇÃO do motorista ou terceiro envolvido).

            **5. PROVIDÊNCIAS ADOTADAS & SOLUÇÃO**
            - (Descrever qual foi a solução ou desfecho dado pela equipe de segurança no local, se houve Near Miss registrado ou encaminhamento médico).
            """
            
            try:
                model_gemini = genai.GenerativeModel("gemini-1.5-flash")
                response_gemini = model_gemini.generate_content(prompt_bo)
                
                st.markdown("---")
                st.markdown("### 📄 Documento Compilado (Gemini 1.5 Flash)")
                st.code(response_gemini.text, language="markdown")
                st.success("✨ Boletim gerado com sucesso! Você pode copiar o texto acima e colar no seu sistema ou e-mail de envio.")
            except Exception as e:
                st.error(f"Erro ao gerar o documento com o Gemini: {e}")
