import json
import os
import logging
import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API客户端"""
    
    def __init__(self, config_file: str = "config/ai_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_count = 0
        self.last_request_time = 0
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("成功加载OpenAI配置文件")
                return config
            else:
                logger.warning(f"配置文件不存在: {self.config_file}")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 4000,
                "timeout": 30,
                "retry_count": 3,
                "retry_delay": 1.0
            },
            "default_provider": "openai",
            "enable_safety_check": True,
            "max_concurrent_requests": 10,
            "rate_limit": {
                "requests_per_minute": 60,
                "tokens_per_minute": 90000
            }
        }
    
    async def get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.config["openai"]["timeout"])
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close_session(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_headers(self, provider: str = "openai") -> Dict[str, str]:
        """获取请求头"""
        config = self.config.get(provider, {})
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.get('api_key', '')}"
        }
        
        # Azure OpenAI 需要特殊的头部
        if provider == "azure_openai":
            headers["api-key"] = config.get('api_key', '')
            del headers["Authorization"]
        
        return headers
    
    def get_url(self, provider: str = "openai") -> str:
        """获取API URL"""
        config = self.config.get(provider, {})
        base_url = config.get('base_url', '')
        
        if provider == "azure_openai":
            api_version = config.get('api_version', '2024-02-01')
            return f"{base_url}/openai/deployments/{config.get('model', 'gpt-4')}/chat/completions?api-version={api_version}"
        else:
            return f"{base_url}/chat/completions"
    
    async def check_rate_limit(self):
        """检查速率限制"""
        current_time = time.time()
        rate_limit = self.config.get("rate_limit", {})
        requests_per_minute = rate_limit.get("requests_per_minute", 60)
        
        # 简单的速率限制检查
        if current_time - self.last_request_time < 60 / requests_per_minute:
            wait_time = 60 / requests_per_minute - (current_time - self.last_request_time)
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def call_openai_api(
        self, 
        prompt: str, 
        provider: str = None,
        temperature: float = None,
        max_tokens: int = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """调用OpenAI API"""
        try:
            # 检查速率限制
            await self.check_rate_limit()
            
            # 使用默认提供商
            if provider is None:
                provider = self.config.get("default_provider", "openai")
            
            provider_config = self.config.get(provider, {})
            
            # 构建请求数据
            request_data = {
                "model": provider_config.get("model", "gpt-4o-mini"),
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature or provider_config.get("temperature", 0.7),
                "max_tokens": max_tokens or provider_config.get("max_tokens", 4000),
                **kwargs
            }
            
            # 获取会话和URL
            session = await self.get_session()
            url = self.get_url(provider)
            headers = self.get_headers(provider)
            
            logger.debug(f"调用{provider} API: {url}")
            
            # 发送请求
            async with session.post(url, json=request_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.debug(f"{provider} API调用成功")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"{provider} API调用失败: {response.status} - {error_text}")
                    
                    # 如果有备用提供商，尝试使用备用提供商
                    fallback_provider = self.config.get("fallback_provider")
                    if fallback_provider and fallback_provider != provider:
                        logger.info(f"尝试使用备用提供商: {fallback_provider}")
                        return await self.call_openai_api(
                            prompt, fallback_provider, temperature, max_tokens, **kwargs
                        )
                    
                    return None
                    
        except Exception as e:
            logger.error(f"OpenAI API调用异常: {e}")
            return None
    
    async def extract_content(self, response: Dict[str, Any]) -> Optional[str]:
        """提取响应内容"""
        try:
            if not response:
                return None
                
            choices = response.get("choices", [])
            if not choices:
                return None
                
            message = choices[0].get("message", {})
            content = message.get("content", "")
            
            return content.strip() if content else None
            
        except Exception as e:
            logger.error(f"提取响应内容失败: {e}")
            return None
    
    async def parse_json_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析JSON响应"""
        try:
            content = await self.extract_content(response)
            if not content:
                return None
            
            # 尝试解析JSON
            # 有时候模型会返回markdown格式的json，需要清理
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            parsed_json = json.loads(content)
            return parsed_json
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"原始内容: {content}")
            return None
        except Exception as e:
            logger.error(f"解析JSON响应失败: {e}")
            return None
    
    def get_token_usage(self, response: Dict[str, Any]) -> Dict[str, int]:
        """获取Token使用情况"""
        try:
            usage = response.get("usage", {})
            return {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0)
            }
        except Exception as e:
            logger.error(f"获取Token使用情况失败: {e}")
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = await self.call_openai_api("Hello, this is a health check.")
            if response:
                return {
                    "status": "healthy",
                    "provider": self.config.get("default_provider", "openai"),
                    "model": self.config.get("openai", {}).get("model", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "API调用失败",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# 创建全局实例
openai_client = OpenAIClient() 