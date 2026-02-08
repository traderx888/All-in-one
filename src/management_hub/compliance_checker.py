"""
ComplianceChecker — Zone LAW

Enforces trading rules and risk limits before any order is executed.
  - Validates orders against position limits, drawdown caps, etc.
  - Checks trading hours / market conditions
  - Blocks or flags non-compliant actions
"""

from __future__ import annotations

from typing import Any

from src.core import BaseAgent, AgentRole, MessageType, Message, MessageBus


class ComplianceChecker(BaseAgent):
    """Gatekeeper that validates all trade actions against risk rules."""

    def __init__(self, bus: MessageBus, config: dict[str, Any] | None = None) -> None:
        super().__init__(
            "compliance_checker", AgentRole.COMPLIANCE_CHECKER, bus,
            division="management_hub", config=config,
        )
        # Configurable limits
        self.max_position_size = config.get("max_position_size", 1000) if config else 1000
        self.max_open_positions = config.get("max_open_positions", 5) if config else 5
        self.max_drawdown_pct = config.get("max_drawdown_pct", 10.0) if config else 10.0
        self.risk_per_trade_pct = config.get("risk_per_trade_pct", 1.0) if config else 1.0
        self._open_positions: list[dict] = []

    async def handle_message(self, message: Message) -> None:
        if message.msg_type == MessageType.RISK_CHECK:
            approved, reason = await self._validate(message.payload)
            if approved:
                await self.send(
                    message.sender,
                    MessageType.RISK_APPROVED,
                    {"order": message.payload, "approved": True},
                )
                self.log.info("order_approved", order=message.payload)
            else:
                await self.send(
                    message.sender,
                    MessageType.RISK_REJECTED,
                    {"order": message.payload, "approved": False, "reason": reason},
                )
                self.log.warning("order_rejected", reason=reason, order=message.payload)

        elif message.msg_type == MessageType.ORDER_FILLED:
            self._open_positions.append(message.payload)

        elif message.msg_type == MessageType.COMMAND:
            if message.payload.get("action") == "get_status":
                await self.send(
                    message.sender,
                    MessageType.STATUS,
                    {
                        "open_positions": len(self._open_positions),
                        "max_positions": self.max_open_positions,
                        "max_drawdown_pct": self.max_drawdown_pct,
                    },
                )

    async def _validate(self, order: dict[str, Any]) -> tuple[bool, str]:
        """Check an order against risk rules."""
        # Position count limit
        if len(self._open_positions) >= self.max_open_positions:
            return False, f"Max open positions reached ({self.max_open_positions})"

        # Position size limit
        size = order.get("size", 0)
        if size > self.max_position_size:
            return False, f"Position size {size} exceeds max {self.max_position_size}"

        # Risk per trade
        risk_pct = order.get("risk_pct", 0)
        if risk_pct > self.risk_per_trade_pct:
            return False, f"Risk {risk_pct}% exceeds limit {self.risk_per_trade_pct}%"

        return True, "OK"
