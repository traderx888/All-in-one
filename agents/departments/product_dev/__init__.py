# ============================================================
# Product Development Department
# 產品開發部 - 動態團隊模式
# ============================================================

from .team_templates import Researcher, Foreman, Worker
from .project_factory import ProjectTeamFactory

__all__ = [
    'Researcher',
    'Foreman',
    'Worker',
    'ProjectTeamFactory'
]
