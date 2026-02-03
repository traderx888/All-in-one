"""
============================================================
Base Agent Class
所有 Agent 的基類
============================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid


class AgentStatus(Enum):
    """Agent 狀態"""
    IDLE = "idle"
    BUSY = "busy"
    WAITING = "waiting"
    ERROR = "error"
    TERMINATED = "terminated"


class AgentType(Enum):
    """Agent 類型"""
    PERMANENT = "permanent"      # 常駐 agent
    PROJECT = "project"          # 項目型 agent (短期僱傭)
    CHAIN = "chain"             # 流水線 agent


@dataclass
class AgentContext:
    """Agent 執行上下文"""
    task_id: str
    parent_agent: Optional[str] = None
    department: Optional[str] = None
    project: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentMessage:
    """Agent 間通訊消息"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""
    message_type: str = "task"  # task, report, query, response
    content: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, 10 最高
    timestamp: datetime = field(default_factory=datetime.now)


class BaseAgent(ABC):
    """
    所有 Agent 的抽象基類

    每個 Agent 必須實現:
    - process(): 處理輸入並產生輸出
    - get_system_prompt(): 返回該 Agent 的系統提示詞
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        agent_type: AgentType = AgentType.PERMANENT,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.agent_type = agent_type
        self.model = model
        self.temperature = temperature
        self.status = AgentStatus.IDLE
        self.context: Optional[AgentContext] = None
        self.message_history: List[AgentMessage] = []
        self.created_at = datetime.now()

    @abstractmethod
    def get_system_prompt(self) -> str:
        """返回該 Agent 的系統提示詞"""
        pass

    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        處理輸入並產生輸出

        Args:
            input_data: 輸入數據

        Returns:
            處理結果
        """
        pass

    def set_context(self, context: AgentContext):
        """設置執行上下文"""
        self.context = context

    def receive_message(self, message: AgentMessage):
        """接收消息"""
        self.message_history.append(message)

    def create_message(
        self,
        receiver: str,
        content: Dict[str, Any],
        message_type: str = "task",
        priority: int = 5
    ) -> AgentMessage:
        """創建消息"""
        return AgentMessage(
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            priority=priority
        )

    def update_status(self, status: AgentStatus):
        """更新狀態"""
        self.status = status

    def get_status_report(self) -> Dict[str, Any]:
        """獲取狀態報告"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "status": self.status.value,
            "type": self.agent_type.value,
            "created_at": self.created_at.isoformat(),
            "messages_processed": len(self.message_history)
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, role={self.role}, status={self.status.value})>"
