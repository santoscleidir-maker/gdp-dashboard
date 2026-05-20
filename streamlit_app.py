import io
import json
import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai
import streamlit as st
from PIL import Image

APP_TITLE = "Sentinela Bravo — Skill BO"

# Modelos oficiais e atualizados para a cota gratuita
MODELS_TO_TRY = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash"
]

MAX_IMAGES = 5
MAX_IMAGE_WIDTH = 1280
JPEG_QUALITY = 78

MODEL_HINTS = {
    "🔥 GERAR BOLETIM UNIVERSAL (Qualquer Modelo do Manual)": "Use o modelo mais aderente ao manual para a situação descrita.",
    "📦 Carga Tombada / Peças Molhadas / Danos em Racks": "Exigir dados de carga, transportadora, motorista, MVM, DANFE, rack e destino da avaliação.",
    "❌ Recusa de Carga / Divergência Fiscal / Excesso de Jornada": "Exigir dados de transporte, horários, placas, MVM e justificativas formais.",
    "Acidente de Trânsito / Colisão Interna (Choque ou Abalroamento)": "Exigir veículos, placas, chassi, tipo de impacto, danos por lado e desfecho com CSO/TST/ambulância se houver.",
    "Desvio de Segurança / Quebra de Regra de Ouro (Falta Grave)": "Exigir relato objective, identificação completa, liderança responsável e providências.",
    "Controle de Acesso / Portaria (Notebooks / Instabilidade Ronda)": "Exigir portaria, item recolhido, documentação, guarda de objetos e providência tomada.",
}

def init_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="centered")
    st.markdown(
        """
        <style>
        .main { background-color: #0d1117; }
        h1, h2, h3 { color: #f97316; }
        .subtitle { color: #8b949e; text-align: center; font-size: 1.02rem; margin-bottom: 1.2rem; }
        .section-card { background-color: #161b22; padding: 16px; border-radius: 14px; border: 1px solid #30363d; margin-bottom: 14px; }
        .section-title { color: #f97316; font-size: 1.08rem; font-weight: 700; margin-bottom: 10px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_all_api_keys() -> List[str]:
    keys = []
    possible_secrets = ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]
    for secret_name in possible_secrets:
        key = None
        try:
            key = st.secrets.get(secret_name)
        except Exception:
            key = None
        if not key:
            key = os.getenv(secret_name)
        if key:
            cleaned_key = key.strip().replace('"', '').replace("'", "")
            if cleaned_key and cleaned_key not in keys:
                keys.append(cleaned_key)
    return keys

def compress_image(uploaded_file: Any) -> Tuple[bytes, Image.Image]:
    raw = uploaded_file.read()
    img = Image.open(io.BytesIO(raw))
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.thumbnail((MAX_IMAGE_WIDTH, MAX_IMAGE_WIDTH))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buffer.getvalue(), img

def safe_date_str(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M")

def parse_json_response(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None

def build_prompt(payload: Dict[str, Any]) -> str:
    return f"""
Você é a Skill BO Sentinela Bravo.
Regras: Linguagem clara, factual e sem opinião. Se faltar dado, escreva "NÃO INFORMADO".

Retorne APENAS um JSON puro estruturado:
{{
  "audit": {{ "modelo_identificado": "", "conformidade": "" }},
  "bo": {{ "data_hora_fato": "", "local_exato": "", "dinamica": "", "status": "" }}
}}

Dados: {json.dumps(payload, ensure_ascii=False)}
""".strip()

def render_kv(label: str, value: Any) -> None:
    st.markdown(f"**{label}:** {value}")

def main() -> None:
    init_page()
    api_keys = get_all_api_keys()
    
    if not api_keys:
        st.error("Nenhuma chave configurada. Adicione 'GEMINI_API_KEY' nos Secrets do Streamlit.")
        st.stop()

    st.title("Sentinela Bravo")
    st.caption("Sistema Anti-Quedas com Rotação de Chaves Ativo.")

    with st.form("bo_form"):
        tipo_ocorrencia = st.selectbox("Modelo principal", list(MODEL_HINTS.keys()))
        local_exato = st.text_input("Local exato do fato")
        relato_bruto = st.text_area("Descreva os fatos")
        arquivos = st.file_uploader("Imagens", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        submit = st.form_submit_button("🚀 Gerar BO")

    if submit:
        if not relato_bruto.strip() or not local_exato.strip():
            st.warning("Preencha os campos obrigatórios.")
            st.stop()

        evidencias_pil = []
        for arquivo in arquivos or []:
            _, pil_img = compress_image(arquivo)
            evidencias_pil.append(pil_img)

        payload = {
            "tipo_ocorrencia": tipo_ocorrencia,
            "local_exato": local_exato.strip(),
            "relato_bruto": relato_bruto.strip(),
            "timestamp": safe_date_str(datetime.now())
        }

        parts = [build_prompt(payload)] + evidencias_pil
        parsed = None

        # Rotação de chaves à prova de falhas com Try/Except corrigido
        with st.spinner("Processando relatório com a Skill BO..."):
            for idx, current_key in enumerate(api_keys):
                if parsed:
                    break
                try:
                    genai.configure(api_key=current_key)
                    for model_name in MODELS_TO_TRY:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(parts)
                            if response and hasattr(response, "text"):
                                parsed = parse_json_response(response.text)
                                if parsed:
                                    break
                        except Exception:
                            continue
                except Exception:
                    st.warning(f"Chave {idx+1} instável. Chaveando rotação...")
                    continue

        if not parsed:
            st.error("Cota temporariamente esgotada em todas as chaves gratuitas. Aguarde 60 segundos.")
            st.stop()

        st.success("Boletim Gerado!")
        st.json(parsed)

if __name__ == "__main__":
    main()
