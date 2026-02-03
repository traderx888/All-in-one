"""
============================================================
Message Bus
Agent 間通訊總線
============================================================
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import asyncio
import logging

from .base_agent import AgentMessage

logger = logging.getLogger(__name__)


@dataclass
class MessageRoute:
    """消息路由規則"""
    source_pattern: str      # 來源 agent 模式 (支持 wildcard)
    target_pattern: str      # 目標 agent 模式
    message_types: List[str] # 適用的消息類型
    priority_boost: int = 0  # 優先級加成
    requires_approval: bool = False  # 是否需要審批


class MessageBus:
    """
    中央消息總線

    負責:
    - Agent 間消息路由
    - 消息優先級排序
    - 跨部門通訊審批
    - 消息日誌記錄
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._routes: List[MessageRoute] = []
        self._message_log: List[AgentMessage] = []
        self._approval_handlers: Dict[str, Callable] = {}

    def subscribe(self, agent_id: str, handler: Callable):
        """訂閱消息"""
        self._subscribers[agent_id].append(handler)
        logger.info(f"Agent {agent_id} subscribed to message bus")

    def unsubscribe(self, agent_id: str, handler: Optional[Callable] = None):
        """取消訂閱"""
        if handler:
            self._subscribers[agent_id].remove(handler)
        else:
            del self._subscribers[agent_id]

    def add_route(self, route: MessageRoute):
        """添加路由規則"""
        self._routes.append(route)

    def set_approval_handler(self, route_id: str, handler: Callable):
        """設置審批處理器"""
        self._approval_handlers[route_id] = handler

    async def publish(self, message: AgentMessage) -> bool:
        """
        發布消息

        Returns:
            是否成功發送
        """
        # 記錄消息
        self._message_log.append(message)

        # 檢查路由規則
        for route in self._routes:
            if self._match_pattern(message.sender, route.source_pattern):
                if route.requires_approval:
                    approved = await self._request_approval(message, route)
                    if not approved:
                        logger.warning(f"Message {message.id} rejected by approval")
                        return False
                message.priority += route.priority_boost

        # 加入優先級隊列 (負數因為 PriorityQueue 是最小堆)
        await self._message_queue.put((-message.priority, message))

        # 異步分發
        asyncio.create_task(self._dispatch(message))

        return True

    async def _dispatch(self, message: AgentMessage):
        """分發消息到目標 agent"""
        if message.receiver in self._subscribers:
            for handler in self._subscribers[message.receiver]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error dispatching message to {message.receiver}: {e}")
        else:
            logger.warning(f"No subscriber found for agent: {message.receiver}")

    async def _request_approval(self, message: AgentMessage, route: MessageRoute) -> bool:
        """請求消息審批"""
        # 默認由 NewTaskManager 審批跨部門通訊
        handler = self._approval_handlers.get("default")
        if handler:
            return await handler(message, route)
        return True  # 無審批處理器時默認通過

    def _match_pattern(self, value: str, pattern: str) -> bool:
        """匹配模式 (支持 * wildcard)"""
        if pattern == "*":
            return True
        if pattern.endswith("*"):
            return value.startswith(pattern[:-1])
        return value == pattern

    def get_message_log(
        self,
        sender: Optional[str] = None,
        receiver: Optional[str] = None,
        limit: int = 100
    ) -> List[AgentMessage]:
        """獲取消息日誌"""
        logs = self._message_log
        if sender:
            logs = [m for m in logs if m.sender == sender]
        if receiver:
            logs = [m for m in logs if m.receiver == receiver]
        return logs[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """獲取統計信息"""
        return {
            "total_messages": len(self._message_log),
            "active_subscribers": len(self._subscribers),
            "routes_configured": len(self._routes),
            "queue_size": self._message_queue.qsize()
        }
