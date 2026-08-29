from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class TrajectoryEntry:
    agent_name: str
    action: str
    tool_used: Optional[str]
    input_summary: str
    result_summary: str
    finding: Optional[str]
    confidence: float
    duration_ms: float
    timestamp: str

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.trajectory: List[TrajectoryEntry] = []

    def log(
        self,
        action: str,
        tool_used: Optional[str] = None,
        input_summary: str = "",
        result_summary: str = "",
        finding: Optional[str] = None,
        confidence: float = 1.0,
        duration_ms: float = 0.0
    ):
        """Record an action in the agent trajectory."""
        entry = TrajectoryEntry(
            agent_name=self.name,
            action=action,
            tool_used=tool_used,
            input_summary=input_summary,
            result_summary=result_summary,
            finding=finding,
            confidence=round(confidence, 2),
            duration_ms=round(duration_ms, 2),
            timestamp=datetime.utcnow().isoformat()
        )
        self.trajectory.append(entry)

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent step and return updated context."""
        pass
