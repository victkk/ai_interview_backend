import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptManager:
    """Prompt模板管理器"""
    
    def __init__(self, prompts_file: str = "data/prompts.json"):
        self.prompts_file = prompts_file
        self.prompts: Dict[str, Any] = {}
        self.load_prompts()
    
    def load_prompts(self) -> None:
        """加载Prompt模板"""
        try:
            # 确保数据目录存在
            os.makedirs(os.path.dirname(self.prompts_file), exist_ok=True)
            
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.prompts = data.get('prompt_templates', {})
                logger.info(f"成功加载 {len(self.prompts)} 个Prompt模板")
            else:
                logger.warning(f"Prompt文件不存在: {self.prompts_file}")
                self.prompts = {}
        except Exception as e:
            logger.error(f"加载Prompt模板失败: {e}")
            self.prompts = {}
    
    def get_prompt(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取指定的Prompt模板"""
        return self.prompts.get(template_id)
    
    def format_prompt(self, template_id: str, **kwargs) -> Optional[str]:
        """格式化Prompt模板"""
        try:
            template = self.get_prompt(template_id)
            if not template:
                logger.error(f"未找到Prompt模板: {template_id}")
                return None
            
            content = template.get('template_content', '')
            if not content:
                logger.error(f"Prompt模板内容为空: {template_id}")
                return None
            
            # 格式化模板
            formatted_content = content.format(**kwargs)
            logger.debug(f"成功格式化Prompt模板: {template_id}")
            return formatted_content
            
        except KeyError as e:
            logger.error(f"Prompt模板格式化失败，缺少参数: {e}")
            return None
        except Exception as e:
            logger.error(f"Prompt模板格式化失败: {e}")
            return None
    
    def list_prompts(self) -> Dict[str, str]:
        """列出所有可用的Prompt模板"""
        return {
            template_id: template.get('template_name', 'Unknown')
            for template_id, template in self.prompts.items()
        }
    
    def get_prompt_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """获取Prompt模板信息"""
        template = self.get_prompt(template_id)
        if not template:
            return None
        
        return {
            'template_id': template.get('template_id'),
            'template_name': template.get('template_name'),
            'template_type': template.get('template_type'),
            'version': template.get('version'),
        }
    
    def reload_prompts(self) -> bool:
        """重新加载Prompt模板"""
        try:
            self.load_prompts()
            return True
        except Exception as e:
            logger.error(f"重新加载Prompt模板失败: {e}")
            return False


# 创建全局实例
prompt_manager = PromptManager() 