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

# Ordem de prioridade dos modelos para o fallback
MODELS_TO_TRY = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash-lite"
]

MAX_IMAGES = 5
MAX_IMAGE_WIDTH = 1280
JPEG_QUALITY = 78

MODEL_HINTS = {
    "🔥 GERAR BOLETIM UNIVERSAL (Qualquer Modelo do Manual)": "Use o modelo mais aderente ao manual para a situação descrita.",
    "📦 Carga Tombada / Peças Molhadas / Danos em Racks": "Exigir dados de carga, transportadora, motorista, MVM, DANFE, rack e destino da avaliação.",
    "❌ Recusa de Carga / Divergência Fiscal / Excesso de Jornada": "Exigir dados de transporte, horários, placas, MVM e justificativas formais.",
    "Acidente de Trânsito / Colisão Interna (Choque ou Abalroamento)": "Exigir veículos, placas, chassi, tipo de impacto, danos por lado e desfecho com CSO/TST/ambulância se houver.",
    "Desvio de Segurança / Quebra de Regra de Ouro (Falta Grave)": "Exigir relato objetivo, identificação completa, liderança responsável e providências.",
    "Controle de Acesso / Portaria (Notebooks / Instabilidade Ronda)": "Exigir portaria, item recolhido, documentação, guarda de objetos e providência tomada.",
}

def init_page() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🛡️", layout="centered")
    st.markdown(
        """
        <style>
        .main { background-color: #0d1117; }
        h1, h2, h3 { color: #f97316; }
        .subtitle {
            color: #8b949e;
            text-align: center;
            font-size: 1.02rem;
            margin-bottom: 1.2rem;
        }
        .section-card {
            background-color: #161b22;
            padding: 16px;
            border-radius: 14px;
            border: 1px solid #30363d;
            margin-bottom: 14px;
        }
        .section-title {
            color: #f97316;
            font-size: 1.08rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def get_all_api_keys() -> List[str]:
    """Busca todas as chaves configuradas nos Secrets (GEMINI_API_KEY, GEMINI_API_KEY_2, etc)"""
    keys = []
    
    # Lista de possíveis nomes de chaves nos Secrets
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
            # Limpa caracteres invisíveis, aspas ou espaços colados pelo celular
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
        return json
