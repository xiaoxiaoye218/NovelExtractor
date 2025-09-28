"""
统一模型路由系统
支持多厂商API调用的统一接口
"""

import json
import time
from typing import Dict, Any, Optional


# 导入配置
import sys
import asyncio
import json
import google.generativeai as genai
from openai import AsyncOpenAI
from typing import Any, Dict, Optional, Union, List

from utils.paths import get_config_path

# 从 JSON 文件加载配置（统一处理开发和打包场景）
with open(get_config_path(), 'r', encoding='utf-8') as f:
    config = json.load(f)

# 提取配置变量
PROVIDER_CONFIG = config.get('PROVIDER_CONFIG', {})
DEFAULT_SYSTEM_PROMPT = config.get('DEFAULT_SYSTEM_PROMPT', "")
DEFAULT_PROVIDER = config.get('DEFAULT_PROVIDER', 'zhipu')
DEFAULT_MODEL_NAME = config.get('DEFAULT_MODEL_NAME', 'glm-4.5')
DEFAULT_STREAM = config.get('DEFAULT_STREAM', False)
DEFAULT_TEMPERATURE = config.get('DEFAULT_TEMPERATURE', None)
DEFAULT_TOP_P = config.get('DEFAULT_TOP_P', None)
DEFAULT_MAX_TOKENS = config.get('DEFAULT_MAX_TOKENS', 32000)
DEFAULT_DOUBAO_THINKING = config.get('DEFAULT_DOUBAO_THINKING', 'disabled')


class AsyncOpenAICompatibleClient:
    """异步OpenAI SDK兼容客户端"""
    
    def __init__(self, api_key: str, base_url: str):
        # OpenAI SDK 使用秒作为单位，
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=900
        )
    
    async def create_completion(self, **kwargs) -> Any:
        """创建完成请求"""
        model_name = kwargs.get("model", "")
        message = kwargs.get("message", "")
        system_prompt = kwargs.get("system_prompt")
        stream = kwargs.get("stream", True)
        temperature = kwargs.get("temperature")
        top_p = kwargs.get("top_p")
        max_tokens = kwargs.get("max_tokens")
        
        # 构建消息
        messages = []
        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        # 构建请求参数
        params = {
            "model": model_name,
            "messages": messages,
            "stream": stream,
        }
        
        # 只在显式指定时添加可选参数
        if temperature is not None:
            params["temperature"] = temperature
        if top_p is not None:
            params["top_p"] = top_p
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        
        return await self.client.chat.completions.create(**params)
        #等待 xxx 这个异步操作完成，然后将它的最终结果作为当前函数的返回值返回
        #在外部调用create_completion这个函数的时候，执行到返回值这一步时，释放控制权，然后等到响应完成再执行返回返回值
        #openai sdk的stream是作为参数传递进去，而gemini的stream调用需要不同的方法
    
    def extract_response(self, response) -> Dict[str, str]:
        """提取响应内容"""
        message = response.choices[0].message
        return {
            "content": message.content or "",
            "reasoning_content": getattr(message, 'reasoning_content', '') or ""
        }
    
    def extract_streaming_response(self, chunk) -> Dict[str, str]:
        """提取流式响应内容"""
        if not chunk.choices or len(chunk.choices) == 0:
            return {"content": "", "reasoning_content": ""}
            
        delta = chunk.choices[0].delta
        return {
            "content": delta.content or "",
            "reasoning_content": getattr(delta, 'reasoning_content', '') or ""
        }


class AsyncGoogleClient:
    """异步Google Gemini官方客户端（支持思维链）"""
    
    def __init__(self, api_key: str, base_url: str = None):
        # google-genai 使用毫秒作为单位，5分钟 = 300000毫秒
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=900000, base_url=base_url)
        )
    
    async def create_completion(self, **kwargs) -> Any:
        """创建完成请求（默认开启思维链）"""
        model_name = kwargs.get("model", "")
        message = kwargs.get("message", "")
        system_prompt = kwargs.get("system_prompt")
        stream = kwargs.get("stream", True)
        temperature = kwargs.get("temperature")
        top_p = kwargs.get("top_p")
        max_output_tokens = kwargs.get("max_tokens")
        
        # 构建内容列表，统一使用 list[types.Content] 格式
        contents = []
        
        # 添加用户消息作为 Content 对象
        user_content = types.Content(
            role="user",
            parts=[types.Part(text=message)]
        )
        contents.append(user_content)
        
        # 构建配置参数（默认开启思维链）
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True
            )
        )
        
        # 只在显式指定时添加参数
        if max_output_tokens is not None:
            config.max_output_tokens = max_output_tokens
        if temperature is not None:
            config.temperature = temperature
        if top_p is not None:
            config.top_p = top_p
        
        # 添加系统提示词（Gemini 使用 system_instruction）
        if system_prompt is not None:
            config.system_instruction = system_prompt
        
        # 根据是否启用流式响应选择不同的方法
        if stream:
            return await self.client.aio.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=config
            )
        else:
            return await self.client.aio.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
    
    def extract_response(self, response) -> Dict[str, str]:
        """提取响应内容（包括思维链）"""
        content_parts = []
        reasoning_parts = []
        
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.text:
                        if hasattr(part, 'thought') and part.thought:
                            reasoning_parts.append(part.text)
                        else:
                            content_parts.append(part.text)
        
        return {
            "content": "".join(content_parts),
            "reasoning_content": "".join(reasoning_parts)
        }
    
    def extract_streaming_response(self, chunk) -> Dict[str, str]:
        """提取流式响应内容（包括思维链）"""
        content_parts = []
        reasoning_parts = []
        
        if chunk.candidates and len(chunk.candidates) > 0:
            candidate = chunk.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.text:
                        if hasattr(part, 'thought') and part.thought:
                            reasoning_parts.append(part.text)
                        else:
                            content_parts.append(part.text)
        
        return {
            "content": "".join(content_parts),
            "reasoning_content": "".join(reasoning_parts)
        }


class ClientFactory:
    """客户端工厂类"""
    
    @staticmethod
    def create_client(provider_config: Dict[str, Any]) -> Any:
        """创建客户端实例"""
        api_key = provider_config["api_key"]
        base_url = provider_config["base_url"]
        client_type = provider_config["type"]
        
        if client_type == "gemini":
            return AsyncGoogleClient(api_key, base_url)
        elif client_type == "openai":
            return AsyncOpenAICompatibleClient(api_key, base_url)
        else:
            raise ValueError(f"不支持的客户端类型: {client_type}")


class ModelRouter:
    """统一模型路由类"""
    
    def get_client(self, model_name: str, provider: str):
        """根据厂商获取对应的客户端"""
        if provider not in PROVIDER_CONFIG:
            raise ValueError(f"不支持的厂商: {provider}")
        return ClientFactory.create_client(PROVIDER_CONFIG[provider])
    
    async def chat(self, 
                   model_name: str,
                   provider: str,
                   message: str) -> Dict[str, Any]:
        """统一聊天接口
        
        Args:
            model_name: 模型名称（必需）
            provider: 指定模型平台（必需）
            message: 用户消息（必需）
        Returns:
            Dict包含响应内容或错误信息
        """
        
        # 所有配置参数都直接从config.py读取
            
        # 获取客户端
        client = self.get_client(model_name, provider)
        
        # 构建参数（直接从config读取所有参数）
        params = {
            "model": model_name,
            "message": message,
            "system_prompt": DEFAULT_SYSTEM_PROMPT,
            "stream": DEFAULT_STREAM,
            "temperature": DEFAULT_TEMPERATURE,
            "top_p": DEFAULT_TOP_P,
            "max_tokens": DEFAULT_MAX_TOKENS,
            
        }
        # 仅当 provider 是 doubao 时，才添加 thinking 字段
        if provider == "doubao":
            params["thinking"] = {
                "type": DEFAULT_DOUBAO_THINKING,  # 或根据需求改为 "auto" / "disabled"
            }
        
        try:
            if DEFAULT_STREAM:
                return await self._handle_streaming_response(client, params)
            else:
                return await self._handle_normal_response(client, params)
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _handle_streaming_response(self, client, params):
        """处理异步流式响应"""
        try:
            response = await client.create_completion(**params)

            async def async_chunk_generator():
                async for chunk in response:
                    chunk_data = client.extract_streaming_response(chunk)
                    yield chunk_data

            return {
                "chunks": async_chunk_generator(),
                "success": True,
                "model": params["model"]
            }

        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def _handle_normal_response(self, client, params):
        """处理异步普通响应"""
        try:
            response = await client.create_completion(**params)
            response_data = client.extract_response(response)
            
            return {
                "content": response_data["content"],
                "reasoning_content": response_data["reasoning_content"],
                "success": True,
                "model": params["model"]
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}

if __name__ == "__main__":
    import asyncio
    
    async def main():
        router = ModelRouter()
        response = await router.chat("doubao-seed-1-6-thinking-250715", "doubao", "你好")
        print(response)
    
    asyncio.run(main())
