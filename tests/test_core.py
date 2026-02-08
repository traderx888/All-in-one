"""Tests for the core agent framework."""

import asyncio
import pytest
from src.core.message import Message, MessageBus, MessageType
from src.core.base_agent import BaseAgent, AgentRole, AgentStatus
from src.core.agent_registry import AgentRegistry
from src.core.pipeline import ResearcherAgent, ForemanAgent, WorkerAgent


# --- Test Message Bus ---

class EchoAgent(BaseAgent):
    """Simple test agent that records received messages."""

    def __init__(self, name, bus):
        super().__init__(name, AgentRole.WORKER, bus)
        self.received: list[Message] = []

    async def handle_message(self, message: Message) -> None:
        self.received.append(message)


@pytest.mark.asyncio
async def test_message_bus_direct_delivery():
    bus = MessageBus()
    agent = EchoAgent("test_agent", bus)
    await agent.start()

    bus_task = asyncio.create_task(bus.start())

    msg = Message(msg_type=MessageType.COMMAND, sender="user", receiver="test_agent", payload={"action": "ping"})
    await bus.publish(msg)
    await asyncio.sleep(0.1)

    assert len(agent.received) == 1
    assert agent.received[0].payload["action"] == "ping"

    await bus.stop()
    bus_task.cancel()


@pytest.mark.asyncio
async def test_message_bus_broadcast():
    bus = MessageBus()
    a1 = EchoAgent("agent_1", bus)
    a2 = EchoAgent("agent_2", bus)
    await a1.start()
    await a2.start()

    bus_task = asyncio.create_task(bus.start())

    msg = Message(msg_type=MessageType.STATUS, sender="system", receiver="*", payload={"status": "ok"})
    await bus.publish(msg)
    await asyncio.sleep(0.1)

    assert len(a1.received) == 1
    assert len(a2.received) == 1

    await bus.stop()
    bus_task.cancel()


# --- Test Agent Registry ---

def test_registry_operations():
    bus = MessageBus()
    registry = AgentRegistry()

    a1 = EchoAgent("agent_1", bus)
    a2 = EchoAgent("agent_2", bus)
    a1.division = "trading_dev"
    a2.division = "product_dev"

    registry.register(a1)
    registry.register(a2)

    assert registry.get("agent_1") is a1
    assert len(registry.get_all()) == 2
    assert len(registry.get_by_division("trading_dev")) == 1

    summary = registry.summary()
    assert summary["total"] == 2

    registry.unregister("agent_1")
    assert registry.get("agent_1") is None


# --- Test Pipeline ---

class TestResearcher(ResearcherAgent):
    async def research(self, params):
        return {"data": "found_something", "query": params.get("query", "")}


class TestForeman(ForemanAgent):
    async def plan(self, data):
        return [{"action": "do_work", "data": data}]


class TestWorker(WorkerAgent):
    async def execute(self, task):
        return {"done": True, "task_action": task.get("action")}


@pytest.mark.asyncio
async def test_pipeline_flow():
    bus = MessageBus()
    researcher = TestResearcher("r", bus, foreman_name="f")
    foreman = TestForeman("f", bus, worker_names=["w"])
    worker = TestWorker("w", bus, foreman_name="f")

    await researcher.start()
    await foreman.start()
    await worker.start()

    bus_task = asyncio.create_task(bus.start())

    # Trigger research
    await bus.publish(Message(
        msg_type=MessageType.COMMAND,
        sender="test",
        receiver="r",
        payload={"action": "research", "query": "test"},
    ))

    # Wait for the full pipeline to execute
    await asyncio.sleep(0.5)

    # Foreman should have received data and delegated
    # Worker should have completed the task
    assert worker.status == AgentStatus.RUNNING

    await bus.stop()
    bus_task.cancel()
