"""
设置管理模块 - 管理应用配置
"""

import os
import json
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from pydantic import BaseModel

from config import BASE_DIR
from .security import verify_csrf_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])

# 配置文件路径
SETTINGS_FILE = os.path.join(BASE_DIR, ".doclite_settings.json")

class AppSettings(BaseModel):
    """应用设置模型"""
    # 应用 Logo
    app_name: str = "DocLite"
    app_icon: str = ""  # base64 编码的图标或 URL
    
    # 向量模型配置
    embedding_provider: str = "local"  # local, ollama
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_api_url: str = "http://localhost:11434"  # Ollama 地址
    embedding_api_model: str = ""  # Ollama 模型名称
    
    # 对话模型配置
    api_provider: str = "ollama"  # ollama, openai, custom
    api_base_url: str = "http://localhost:11434"  # Ollama 默认地址
    api_key: str = ""  # OpenAI API Key
    api_model: str = "qwen2:1.5b"  # 默认模型

    # OCR 配置
    ocr_enabled: bool = True
    ocr_language: str = "chi_sim+eng"  # Tesseract 语言代码

def load_settings() -> AppSettings:
    """加载设置"""
    if not os.path.exists(SETTINGS_FILE):
        return AppSettings()
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return AppSettings(**data)
    except Exception as e:
        logger.error(f"加载设置失败: {e}")
        return AppSettings()

def save_settings(settings: AppSettings):
    """保存设置"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings.model_dump(), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存设置失败: {e}")
        raise

@router.get("/")
def get_settings():
    """获取当前设置"""
    settings = load_settings()
    # 隐藏 API Key 的完整内容
    settings_dict = settings.model_dump()
    if settings_dict.get("api_key"):
        settings_dict["api_key"] = "***" + settings_dict["api_key"][-4:] if len(settings_dict["api_key"]) > 4 else "***"
    return {"status": "ok", "settings": settings_dict}

@router.post("/")
def update_settings(
    settings: AppSettings,
    csrf_token: str = Depends(verify_csrf_token)
):
    """更新设置"""
    try:
        save_settings(settings)
        return {"status": "ok", "message": "设置已保存"}
    except Exception as e:
        logger.error(f"更新设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新设置失败: {str(e)}")

@router.post("/logo")
def update_logo(
    logo_data: str = Query(..., description="Logo 数据 (base64 或 URL)"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """更新应用 Logo"""
    settings = load_settings()
    settings.app_icon = logo_data
    save_settings(settings)
    return {"status": "ok", "message": "Logo 已更新"}

@router.post("/embedding-model")
def update_embedding_model(
    model_name: str = Query(..., description="Embedding 模型名称"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """更新 Embedding 模型"""
    settings = load_settings()
    settings.embedding_model = model_name
    save_settings(settings)
    return {"status": "ok", "message": "Embedding 模型已更新"}

@router.post("/api-config")
def update_api_config(
    provider: str = Query(..., description="API 提供商 (ollama/openai/custom)"),
    base_url: str = Query("", description="API 基础 URL"),
    api_key: str = Query("", description="API Key"),
    model: str = Query("", description="模型名称"),
    csrf_token: str = Depends(verify_csrf_token)
):
    """更新 API 配置"""
    settings = load_settings()
    settings.api_provider = provider
    settings.api_base_url = base_url
    settings.api_key = api_key
    settings.api_model = model
    save_settings(settings)
    return {"status": "ok", "message": "API 配置已更新"}

@router.get("/providers")
def get_providers():
    """获取支持的 API 提供商列表"""
    return {
        "status": "ok",
        "providers": [
            {
                "id": "ollama",
                "name": "Ollama (本地)",
                "description": "本地运行的 Ollama 服务",
                "default_url": "http://localhost:11434",
                "requires_key": False
            },
            {
                "id": "openai",
                "name": "OpenAI",
                "description": "OpenAI GPT 模型",
                "default_url": "https://api.openai.com/v1",
                "requires_key": True
            },
            {
                "id": "custom",
                "name": "自定义 API",
                "description": "任何 OpenAI 兼容的 API",
                "default_url": "",
                "requires_key": True
            }
        ]
    }

@router.get("/embedding-models")
def get_embedding_models():
    """获取支持的 Embedding 模型列表"""
    return {
        "status": "ok",
        "providers": [
            {
                "id": "local",
                "name": "本地模型",
                "description": "使用 sentence-transformers 本地运行",
                "models": [
                    {"id": "paraphrase-multilingual-MiniLM-L12-v2", "name": "MiniLM-L12 (多语言, 118MB)", "size": "118MB"},
                    {"id": "all-MiniLM-L6-v2", "name": "MiniLM-L6 (英文, 80MB)", "size": "80MB"},
                    {"id": "bge-small-zh-v1.5", "name": "BGE-small 中文 (80MB)", "size": "80MB"},
                    {"id": "bge-base-zh-v1.5", "name": "BGE-base 中文 (400MB)", "size": "400MB"}
                ]
            },
            {
                "id": "ollama",
                "name": "Ollama (本地服务)",
                "description": "使用本地 Ollama 服务生成向量",
                "models": [
                    {"id": "nomic-embed-text", "name": "nomic-embed-text (274MB)", "size": "274MB"},
                    {"id": "mxbai-embed-large", "name": "mxbai-embed-large (670MB)", "size": "670MB"},
                    {"id": "all-minilm", "name": "all-minilm (23MB)", "size": "23MB"}
                ]
            }
        ]
    }

@router.get("/ocr-languages")
def get_ocr_languages():
    """获取支持的 OCR 语言列表"""
    return {
        "status": "ok",
        "languages": [
            {"id": "eng", "name": "English", "description": "英文"},
            {"id": "chi_sim", "name": "简体中文", "description": "简体中文"},
            {"id": "chi_tra", "name": "繁體中文", "description": "繁体中文"},
            {"id": "chi_sim+eng", "name": "中英混合", "description": "中英文混合识别（推荐）"},
            {"id": "jpn", "name": "日本語", "description": "日文"},
            {"id": "kor", "name": "한국어", "description": "韩文"},
        ]
    }
