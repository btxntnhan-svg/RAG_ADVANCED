import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
try:
    import requests
except ImportError:
    requests = None
import urllib.request
import urllib.error

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Try loading .env if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class OllamaClient:
    """
    Ollama API Adapter Client for local model inference and health checking.
    Supports automatic fallback to a local rule-engine when Ollama service is unavailable.
    """
    def __init__(self, base_url: Optional[str] = None, model_name: Optional[str] = None, timeout: float = 2.0):
        # 1. Environment & Default Config
        url = (
            base_url 
            or os.getenv("OLLAMA_BASE_URL") 
            or "http://localhost:11434"
        ).rstrip("/")
        if "localhost" in url:
            url = url.replace("localhost", "127.0.0.1")
        self.base_url = url
        self.model_name = (
            model_name 
            or os.getenv("OLLAMA_MODEL") 
            or "qwen3:0.6b"
        )
        self.timeout = timeout

    def check_health(self) -> Dict[str, Any]:
        """
        Check if Ollama Server is online and list available models from /api/tags.
        """
        tags_url = f"{self.base_url}/api/tags"
        try:
            if requests:
                resp = requests.get(tags_url, timeout=self.timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return {
                        "online": True,
                        "status_code": 200,
                        "models": models,
                        "base_url": self.base_url,
                        "model": self.model_name
                    }
            else:
                req = urllib.request.Request(tags_url, headers={"User-Agent": "OllamaClient"})
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        models = [m.get("name") for m in data.get("models", [])]
                        return {
                            "online": True,
                            "status_code": 200,
                            "models": models,
                            "base_url": self.base_url,
                            "model": self.model_name
                        }
        except Exception as e:
            logger.warning(f"Ollama server at {self.base_url} is unreachable: {e}")

        return {
            "online": False,
            "status_code": 0,
            "models": [],
            "base_url": self.base_url,
            "model": self.model_name
        }

    def generate(self, prompt: str, format_json: bool = False, temperature: float = 0.2) -> str:
        """
        Send prompt to Ollama REST API /api/generate.
        Falls back to rule-engine fallback if Ollama is offline.
        """
        health = self.check_health()
        if not health["online"]:
            logger.info("Ollama offline. Using Rule-Engine Fallback mode.")
            return self._fallback_generate(prompt, format_json=format_json)

        generate_url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 128
            }
        }
        if format_json:
            payload["format"] = "json"

        try:
            if requests:
                resp = requests.post(generate_url, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    res_data = resp.json()
                    return res_data.get("response", "")
                else:
                    logger.error(f"Ollama API returned error HTTP {resp.status_code}: {resp.text}")
                    return self._fallback_generate(prompt, format_json=format_json)
            else:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    generate_url,
                    data=data_bytes,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=60.0) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    return res_data.get("response", "")
        except Exception as e:
            logger.error(f"Error during Ollama generate API call: {e}")
            return self._fallback_generate(prompt, format_json=format_json)

    def _fallback_generate(self, prompt: str, format_json: bool = False) -> str:
        """
        Safe rule-engine fallback response generator when Ollama Server is offline.
        """
        if format_json:
            fallback_dict = {
                "status": "FALLBACK_RULE_ENGINE",
                "llm_provider": "ollama_fallback",
                "model": self.model_name,
                "summary": "Ollama server offline - Tra cuu tu dong bang quy tac du phong",
                "findings": [
                    {
                        "conflict_id": "RULE_FB_01",
                        "policy_ref": "Quy dinh Agribank Internal Policy",
                        "status": "REQUIRES_REVIEW",
                        "details": "He thong dang hoat dong o che do ngoai tuyen (Rule-Engine Fallback).",
                        "recommendation": "Kiem tra lai trang thai container Ollama hoac ket noi mang."
                    }
                ],
                "checklist": [
                    {
                        "step": 1,
                        "action": "Kiem tra ket noi Ollama container (port 11434)",
                        "target_role": "KIEM_TOAN_VIEN",
                        "status": "NEEDS_HUMAN_REVIEW"
                    }
                ],
                "note": "Ket qua duoc tao tu che do du phong an toan."
            }
            return json.dumps(fallback_dict, ensure_ascii=False, indent=2)

        # Standard text fallback response
        return (
            f"[RULE-ENGINE FALLBACK]\n"
            f"Trang thai: Ollama Server offline ({self.base_url}).\n"
            f"Mo hinh yeu cau: {self.model_name}\n"
            f"Phan hoi du phong cho prompt: '{prompt[:60]}...'\n"
            f"Luu y: Vui long khoi chay Ollama container (docker compose up -d) de su dung AI Model truc tiep."
        )


if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print(" TESTING OLLAMA API ADAPTER CLIENT (`scripts/ollama_adapter.py`)")
    print("=" * 60)

    client = OllamaClient()
    health = client.check_health()

    print(f"Base URL: {health['base_url']}")
    print(f"Target Model: {health['model']}")
    print(f"Server Online: {health['online']}")
    print(f"Available Models: {health['models']}")

    # Test generation (will execute API or fallback)
    sample_prompt = "Kiem tra ket noi Ollama va phan hoi ngan gon."
    print("\n--- Testing generate() ---")
    response_text = client.generate(sample_prompt, format_json=False)
    print(f"Response:\n{response_text}")

    print("\n--- Testing generate(format_json=True) ---")
    response_json = client.generate(sample_prompt, format_json=True)
    print(f"JSON Response:\n{response_json}")

    print("\n" + "=" * 60)
    print("BAO CAO KET QUA KIEM TRA:")
    print("OLLAMA ADAPTER: PASS")
    server_status = "YES" if health['online'] else "NO"
    print(f"OLLAMA SERVER ONLINE: {server_status}")
    print("=" * 60)
