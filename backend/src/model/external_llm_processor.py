import logging
import time
import json
import os
import traceback
import requests
from typing import Dict, Any, Optional

# Configurar o logger para o processador externo de LLMs
logger = logging.getLogger("external_llm_processor")

class ExternalLLMProcessor:
    """
    Processador que utiliza APIs de LLMs externos para extrair entidades de domínio a partir de texto de requisitos
    """

    def __init__(self):
        """
        Inicializa o processador com configurações de URLs, modelos e chaves de API
        """
        # URLs e modelos suportados para cada provedor de LLM
        self.openai_api_url = "https://api.openai.com/v1/chat/completions"
        self.openai_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]

        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        self.deepseek_models = ["deepseek-chat", "deepseek-coder"]

        self.qwen_api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.qwen_models = ["qwen-max", "qwen-plus", "qwen-turbo"]

        self.gemini_api_url = (
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        )
        self.gemini_models = ["gemini-pro"]

        # Carregar chaves da API das variáveis de ambiente
        self.env_api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "qwen": os.getenv("QWEN_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY"),
        }

        # Configuração inicial de provedor e modelo
        self.api_key: Optional[str] = None
        self.provider: str = "openai"  # Provedor padrão
        self.model: str = "gpt-3.5-turbo"  # Modelo padrão

        logger.info("Processador ExternalLLMProcessor inicializado")

    def extract_domain_entities(self, requirements_text: str) -> Dict[str, Any]:
        """
        Extrai entidades de domínio a partir do texto de requisitos usando o provedor selecionado

        Args:
            requirements_text (str): Texto com os requisitos (pode conter códigos RF)

        Returns:
            Dict[str, Any]: Resultado com JSON das classes ou mensagem de erro
        """
        start_time = time.time()
        logger.info(
            f"Iniciando extração de entidades com {self.provider}/{self.model}, "
            f"texto de {len(requirements_text)} caracteres"
        )

        # Atualizar chaves de API a partir do ambiente
        current_env = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
            "qwen": os.getenv("QWEN_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY"),
        }
        self.env_api_keys = current_env

        # Registar quais chaves estão configuradas (sem expor valor completo)
        for prov, key in self.env_api_keys.items():
            if key:
                masked = key[:5] + "..." + key[-4:] if len(key) > 10 else "***"
                logger.info(f"Chave {prov} carregada: {masked}")
            else:
                logger.warning(f"Chave {prov} não configurada")

        # Determinar qual chave usar (interna ou da variável de ambiente)
        api_key = self.api_key or self.env_api_keys.get(self.provider)
        if not api_key:
            msg = (
                f"Chave API para provedor '{self.provider}' não configurada. "
                "Defina OPENAI_API_KEY, DEEPSEEK_API_KEY, QWEN_API_KEY ou GEMINI_API_KEY."
            )
            logger.error(msg)
            return {"error": msg}
        self.api_key = api_key
        logger.info(f"Usando chave de API para {self.provider}")

        # Pré-processar texto para destacar requisitos RF, se existirem
        processed = self._preprocess_requirements(requirements_text)

        # Selecionar fluxo de processamento conforme provedor
        if self.provider == "openai":
            return self._process_with_openai(processed)
        if self.provider == "deepseek":
            return self._process_with_deepseek(processed)
        if self.provider == "qwen":
            return self._process_with_qwen(processed)
        if self.provider == "gemini":
            return self._process_with_gemini(processed)

        # Provedor não suportado
        msg = f"Provedor '{self.provider}' não suportado."
        logger.error(msg)
        return {"error": msg}

    def _preprocess_requirements(self, requirements_text: str) -> str:
        """
        Destaca e reformata códigos de requisito no formato RFxx. Texto...

        Args:
            requirements_text (str): Texto original de requisitos

        Returns:
            str: Texto com requisitos RF numerados ou original
        """
        import re
        pattern = r"RF\d+\.\s*(.*?)(?=RF\d+\.|$)"
        matches = re.findall(pattern, requirements_text, re.DOTALL)
        if matches:
            processed = []
            rf_nums = re.findall(r"RF(\d+)", requirements_text)
            for txt, num in zip(matches, rf_nums):
                processed.append(f"Requisito #{num}: {txt.strip()}")
            return "\n\n".join(processed)
        return requirements_text

    def _process_with_openai(self, text: str) -> Dict[str, Any]:
        """
        Envia pedido à API OpenAI Chat Completions e extrai JSON de resposta
        """
        start = time.time()
        try:
            # Construir prompt com instruções claras em Português
            prompt = (
                "Analise os seguintes requisitos e extraia as classes de domínio, atributos e relacionamentos."
                " Forneça apenas JSON estruturado conforme especificado.\n\n"
                f"Requisitos:\n{text}\n\n"
                "Formato de saída (JSON exato, sem texto adicional):\n"
                "{\n"
                "  \"classes\": [\n"
                "    {\n"
                "      \"nome\": \"NomeClasse\",\n"
                "      \"atributos\": [\n"
                "        {\"nome\": \"atributo\", \"tipo\": \"tipoAtributo\"}\n"
                "      ],\n"
                "      \"relacionamentos\": [\n"
                "        {\"tipo\": \"associacao/composicao/heranca\", \"alvo\": \"OutraClasse\", \"cardinalidade\": \"1..n\"}\n"
                "      ]\n"
                "    }\n"
                "  ]\n"
                "}"
            )
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            logger.info(f"Enviando pedido OpenAI (modelo={self.model})")
            resp = requests.post(
                self.openai_api_url,
                json=payload,
                headers=headers,
                timeout=45,
            )
            logger.info(
                f"Resposta OpenAI {resp.status_code} em {time.time() - start:.2f}s"
            )
            if resp.status_code != 200:
                msg = f"Erro OpenAI: {resp.status_code} - {resp.text}"
                logger.error(msg)
                return {"error": msg}
            data = resp.json()
            # Validar existência de escolhas
            if "choices" in data and data["choices"]:
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Conteúdo recebido ({len(content)} caracteres)")
                return self._extract_json_from_response(content)
            msg = "Resposta OpenAI sem 'choices'"
            logger.error(msg)
            return {"error": msg}
        except requests.exceptions.Timeout as e:
            msg = f"Timeout OpenAI: {e}"
            logger.error(msg)
            return {"error": msg}
        except Exception as e:
            logger.error(f"Exceção OpenAI: {traceback.format_exc()}")
            return {"error": str(e)}

    def _process_with_deepseek(self, text: str) -> Dict[str, Any]:
        """
        Envia pedido à API Deepseek e extrai JSON de resposta
        """
        start = time.time()
        try:
            prompt = (
                "Analise os requisitos e extrai JSON conforme formato especificado.\n\n"
                f"{text}\n"
            )
            payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            logger.info(f"Enviando pedido Deepseek (modelo={self.model})")
            resp = requests.post(
                self.deepseek_api_url,
                json=payload,
                headers=headers,
                timeout=45,
            )
            logger.info(f"Resposta Deepseek {resp.status_code} em {time.time() - start:.2f}s")
            if resp.status_code != 200:
                msg = f"Erro Deepseek: {resp.status_code} - {resp.text}"
                logger.error(msg)
                return {"error": msg}
            data = resp.json()
            if "choices" in data and data["choices"]:
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Conteúdo Deepseek recebido ({len(content)} caracteres)")
                return self._extract_json_from_response(content)
            msg = "Resposta Deepseek sem 'choices'"
            logger.error(msg)
            return {"error": msg}
        except Exception as e:
            logger.error(f"Exceção Deepseek: {traceback.format_exc()}")
            return {"error": str(e)}

    def _process_with_qwen(self, text: str) -> Dict[str, Any]:
        """
        Envia pedido à API Qwen (Alibaba Cloud) e extrai JSON de resposta
        """
        start = time.time()
        try:
            prompt = (
                "Analise requisitos e extrai JSON conforme formato especificado.\n\n"
                f"{text}\n"
            )
            payload = {
                "model": self.model,
                "input": {"messages": [{"role": "user", "content": prompt}]},
                "parameters": {"temperature": 0.1},
            }
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            logger.info(f"Enviando pedido Qwen (modelo={self.model})")
            resp = requests.post(
                self.qwen_api_url,
                json=payload,
                headers=headers,
                timeout=45,
            )
            logger.info(f"Resposta Qwen {resp.status_code} em {time.time() - start:.2f}s")
            if resp.status_code != 200:
                msg = f"Erro Qwen: {resp.status_code} - {resp.text}"
                logger.error(msg)
                return {"error": msg}
            data = resp.json()
            # Qwen devolve texto em campo 'output.text'
            if "output" in data and "text" in data["output"]:
                content = data["output"]["text"]
                logger.info(f"Conteúdo Qwen recebido ({len(content)} caracteres)")
                return self._extract_json_from_response(content)
            msg = "Resposta Qwen sem campos esperados"
            logger.error(msg)
            return {"error": msg}
        except Exception as e:
            logger.error(f"Exceção Qwen: {traceback.format_exc()}")
            return {"error": str(e)}

    def _process_with_gemini(self, text: str) -> Dict[str, Any]:
        """
        Envia pedido à API Google Gemini Pro e extrai JSON de resposta
        """
        start = time.time()
        try:
            prompt = (
                "Analise requisitos e extrai JSON conforme formato especificado.\n\n"
                f"{text}\n"
            )
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1, "topP": 0.8, "topK": 40},
            }
            url = f"{self.gemini_api_url}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            logger.info(f"Enviando pedido Gemini (modelo={self.model})")
            resp = requests.post(url, json=payload, headers=headers, timeout=45)
            logger.info(f"Resposta Gemini {resp.status_code} em {time.time() - start:.2f}s")
            if resp.status_code != 200:
                msg = f"Erro Gemini: {resp.status_code} - {resp.text}"
                logger.error(msg)
                return {"error": msg}
            data = resp.json()
            # Extrair texto dos candidatos retornados
            if "candidates" in data and data["candidates"]:
                text_acc = []
                for part in data["candidates"][0]["content"]["parts"]:
                    if "text" in part:
                        text_acc.append(part["text"])
                content = "".join(text_acc)
                logger.info(f"Conteúdo Gemini recebido ({len(content)} caracteres)")
                return self._extract_json_from_response(content)
            msg = "Resposta Gemini sem campos esperados"
            logger.error(msg)
            return {"error": msg}
        except Exception as e:
            logger.error(f"Exceção Gemini: {traceback.format_exc()}")
            return {"error": str(e)}

    def _extract_json_from_response(self, content: str) -> Dict[str, Any]:
        """
        Extrai e valida JSON embutido no texto de resposta do LLM

        Args:
            content (str): Texto bruto retornado pelo LLM

        Returns:
            Dict[str, Any]: Dicionário com 'content' em JSON ou 'error'
        """
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                # Tentar parse JSON
                json.loads(json_str)
                logger.info("JSON válido extraído da resposta")
                return {"content": json_str}
            msg = "Não foi possível encontrar JSON válido na resposta"
            logger.error(msg)
            return {"error": msg}
        except Exception as e:
            msg = f"Erro ao extrair JSON: {e}"
            logger.error(msg)
            return {"error": msg}
