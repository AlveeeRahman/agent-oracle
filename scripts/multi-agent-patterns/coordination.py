"""
Multi-Agent Coordination Utilities

Provides reusable building blocks for multi-agent coordination patterns:
supervisor/orchestrator, peer-to-peer handoffs, consensus mechanisms,
and failure handling with circuit breakers.

Use when: building multi-agent systems that need structured communication,
task delegation, consensus voting, or fault-tolerant agent coordination.

Designed for composability — import individual classes or use the
``if __name__ == "__main__"`` demo to see all patterns in action.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import argparse
import json
import sys
import time
import uuid

__all__ = [
    "MessageType",
    "AgentMessage",
    "AgentCommunication",
    "SupervisorAgent",
    "HandoffProtocol",
    "ConsensusManager",
    "AgentFailureHandler",
]


class MessageType(Enum):
    """Types of messages exchanged between agents."""

    REQUEST = "request"
    RESPONSE = "response"
    HANDOVER = "handover"
    FEEDBACK = "feedback"
    ALERT = "alert"


@dataclass
class AgentMessage:
    """Message exchanged between agents.

    Use when: agents need a structured envelope for inter-agent communication
    that carries sender/receiver identity, type, priority, and payload.
    """

    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requires_response: bool = False
    priority: int = 0  # 0 = normal, higher = more urgent


class AgentCommunication:
    """Communication channel for multi-agent systems.

    Use when: multiple agents need an in-process message bus for sending,
    receiving, and broadcasting messages with history tracking.
    """

    def __init__(self) -> None:
        self.inbox: Dict[str, List[AgentMessage]] = {}
        self.outbox: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []

    def send(self, message: AgentMessage) -> None:
        """Send a message to an agent."""
        if message.receiver not in self.inbox:
            self.inbox[message.receiver] = []
        self.inbox[message.receiver].append(message)
        self.outbox.append(message)
        self.message_history.append(message)

    def receive(self, agent_id: str) -> List[AgentMessage]:
        """Receive all messages for an agent, clearing its inbox."""
        messages = self.inbox.get(agent_id, [])
        self.inbox[agent_id] = []
        return messages

    def broadcast(
        self,
        sender: str,
        message_type: MessageType,
        content: Dict[str, Any],
        receivers: List[str],
    ) -> None:
        """Broadcast a message to multiple agents."""
        for receiver in receivers:
            self.send(
                AgentMessage(
                    sender=sender,
                    receiver=receiver,
                    message_type=message_type,
                    content=content,
                )
            )


# ---------------------------------------------------------------------------
# Supervisor Pattern
# ---------------------------------------------------------------------------


class SupervisorAgent:
    """Central supervisor agent that coordinates worker agents.

    Use when: tasks have clear decomposition and a single coordinator should
    delegate subtasks, track worker status, and aggregate results.
    """

    def __init__(self, name: str, communication: AgentCommunication) -> None:
        self.name = name
        self.communication = communication
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.completed_tasks: List[Dict[str, Any]] = []
        self.current_state: Dict[str, Any] = {}

    def register_worker(self, worker_id: str, capabilities: List[str]) -> None:
        """Register a worker agent with the supervisor."""
        self.workers[worker_id] = {
            "capabilities": capabilities,
            "status": "available",
            "current_task": None,
            "metrics": {"tasks_completed": 0, "avg_response_time": 0.0},
        }

    def decompose_task(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose a task into subtasks.

        Use when: a high-level task needs to be broken into assignable units.
        In production, replace the rule-based logic with LLM-driven planning.
        """
        subtasks: List[Dict[str, Any]] = []
        task_type = task.get("type", "general")

        if task_type == "research":
            subtasks = [
                {"type": "search", "description": "Gather information"},
                {"type": "analyze", "description": "Analyze findings"},
                {"type": "synthesize", "description": "Synthesize results"},
            ]
        elif task_type == "create":
            subtasks = [
                {"type": "plan", "description": "Create plan"},
                {"type": "draft", "description": "Draft content"},
                {"type": "review", "description": "Review and refine"},
            ]
        else:
            subtasks = [
                {
                    "type": "execute",
                    "description": task.get("description", "Execute task"),
                }
            ]

        for subtask in subtasks:
            subtask["parent_task"] = task.get("id")
            subtask["priority"] = task.get("priority", 0)

        return subtasks

    def assign_task(self, subtask: Dict[str, Any], worker_id: str) -> None:
        """Assign a subtask to a worker agent."""
        if worker_id not in self.workers:
            raise ValueError(f"Unknown worker: {worker_id}")

        self.workers[worker_id]["status"] = "busy"
        self.workers[worker_id]["current_task"] = subtask.get("id")

        self._send(
            AgentMessage(
                sender=self.name,
                receiver=worker_id,
                message_type=MessageType.REQUEST,
                content={"action": "execute_task", "task": subtask},
                requires_response=True,
                priority=subtask.get("priority", 0),
            )
        )

    def select_worker(self, subtask: Dict[str, Any]) -> str:
        """Select the best available worker for a subtask.

        Use when: the supervisor needs capability-aware routing with
        load-balancing (fewest completed tasks chosen first).
        """
        required_capability = subtask.get("type", "general")

        candidates = [
            wid
            for wid, info in self.workers.items()
            if info["status"] == "available"
            and required_capability in info["capabilities"]
        ]

        if not candidates:
            candidates = [
                wid
                for wid, info in self.workers.items()
                if info["status"] == "available"
            ]

        if not candidates:
            raise ValueError("No available workers")

        return min(
            candidates,
            key=lambda w: self.workers[w]["metrics"]["tasks_completed"],
        )

    def aggregate_results(
        self, subtask_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate results from completed subtasks."""
        summaries = [
            r.get("summary", "")
            for r in subtask_results
            if r.get("success")
        ]
        successful = sum(
            1 for r in subtask_results if r.get("success", False)
        )
        quality = successful / len(subtask_results) if subtask_results else 0.0

        return {
            "results": subtask_results,
            "summary": " | ".join(summaries),
            "quality_score": quality,
        }

    def run_workflow(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow with supervision.

        Use when: running an end-to-end supervised pipeline that decomposes
        a task, assigns subtasks, collects results, and aggregates them.

        Note: This is a synchronous simulation. Workers do not execute
        asynchronously — each subtask is simulated inline. In production,
        replace ``_simulate_worker_response`` with actual async worker
        execution and message passing.
        """
        subtasks = self.decompose_task(task)

        results: List[Dict[str, Any]] = []
        for subtask in subtasks:
            worker = self.select_worker(subtask)
            self.assign_task(subtask, worker)

            # Simulate worker executing and responding
            response = self._simulate_worker_response(worker, subtask)
            self.communication.send(
                AgentMessage(
                    sender=worker,
                    receiver=self.name,
                    message_type=MessageType.RESPONSE,
                    content=response,
                )
            )
            self.workers[worker]["status"] = "available"
            self.workers[worker]["metrics"]["tasks_completed"] += 1

            messages = self.communication.receive(self.name)
            for msg in messages:
                if msg.message_type == MessageType.RESPONSE:
                    results.append(msg.content)

        final_result = self.aggregate_results(results)

        return {
            "task": task,
            "subtask_results": results,
            "final_result": final_result,
            "success": final_result["quality_score"] >= 0.8,
        }

    def _simulate_worker_response(
        self, worker_id: str, subtask: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate a worker completing a subtask.

        In production, replace with actual agent execution that sends
        the subtask to a worker process and awaits a real response.
        """
        return {
            "success": True,
            "summary": f"{worker_id} completed: {subtask.get('description', subtask.get('type', 'task'))}",
            "worker": worker_id,
            "subtask_type": subtask.get("type"),
        }

    def _send(self, message: AgentMessage) -> None:
        """Send message through the communication channel."""
        self.communication.send(message)


# ---------------------------------------------------------------------------
# Handoff Protocol
# ---------------------------------------------------------------------------


class HandoffProtocol:
    """Protocol for agent-to-agent handoffs.

    Use when: implementing peer-to-peer or swarm patterns where agents
    transfer control and task state to one another.
    """

    def __init__(self, communication: AgentCommunication) -> None:
        self.communication = communication

    def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        context: Dict[str, Any],
        reason: str,
    ) -> AgentMessage:
        """Create a handoff message with transferred context."""
        return AgentMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type=MessageType.HANDOVER,
            content={
                "handoff_reason": reason,
                "transferred_context": context,
                "handoff_timestamp": time.time(),
            },
            priority=1,
        )

    def accept_handoff(self, agent_id: str) -> Optional[AgentMessage]:
        """Accept the first pending handoff for an agent, if any."""
        messages = self.communication.receive(agent_id)

        for msg in messages:
            if msg.message_type == MessageType.HANDOVER:
                return msg

        return None

    def transfer_with_state(
        self,
        from_agent: str,
        to_agent: str,
        state: Dict[str, Any],
        task: Dict[str, Any],
    ) -> bool:
        """Transfer task state from one agent to another.

        Use when: a handoff must carry full task state and progress so the
        receiving agent can resume without re-deriving context.

        Returns True if the receiving agent acknowledged the handoff.
        """
        handoff = self.create_handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            context={
                "task_state": state,
                "task_details": task,
                "progress": state.get("progress", 0),
            },
            reason="task_transfer",
        )

        self.communication.send(handoff)

        # In production, replace sleep with async await + timeout
        time.sleep(0.1)
        ack = self.communication.receive(from_agent)

        return any(
            m.message_type == MessageType.RESPONSE
            and m.content.get("status") == "handoff_received"
            for m in ack
        )


# ---------------------------------------------------------------------------
# Consensus Mechanism
# ---------------------------------------------------------------------------


class ConsensusManager:
    """Manager for multi-agent consensus building.

    Use when: multiple agents must vote on a decision and the system needs
    weighted consensus that accounts for confidence and expertise rather
    than naive majority voting.
    """

    def __init__(self) -> None:
        self.votes: Dict[str, List[Dict[str, Any]]] = {}
        self.debates: Dict[str, List[Dict[str, Any]]] = {}

    def initiate_vote(
        self, topic_id: str, agents: List[str], options: List[str]
    ) -> None:
        """Initiate a voting round on a topic."""
        self.votes[topic_id] = [
            {
                "agent": agent,
                "topic": topic_id,
                "options": options,
                "status": "pending",
            }
            for agent in agents
        ]

    def submit_vote(
        self,
        topic_id: str,
        agent_id: str,
        selection: str,
        confidence: float,
    ) -> None:
        """Submit a vote for a topic with a confidence weight."""
        if topic_id not in self.votes:
            raise ValueError(f"Unknown topic: {topic_id}")

        for vote in self.votes[topic_id]:
            if vote["agent"] == agent_id:
                vote["status"] = "cast"
                vote["selection"] = selection
                vote["confidence"] = confidence
                break

    def calculate_weighted_consensus(self, topic_id: str) -> Dict[str, Any]:
        """Calculate weighted consensus from cast votes.

        Use when: votes are in and the system needs to determine a winner
        weighted by each agent's confidence rather than simple majority.
        Weight = confidence * expertise_factor.
        """
        if topic_id not in self.votes:
            raise ValueError(f"Unknown topic: {topic_id}")

        votes = [
            v for v in self.votes[topic_id] if v.get("status") == "cast"
        ]

        if not votes:
            return {"status": "no_votes", "result": None}

        # Group by selection
        selections: Dict[str, List[Dict[str, Any]]] = {}
        for vote in votes:
            selection = vote["selection"]
            if selection not in selections:
                selections[selection] = []
            selections[selection].append(vote)

        # Calculate weighted score for each selection
        results: Dict[str, Dict[str, Any]] = {}
        for selection, selection_votes in selections.items():
            weighted_sum = sum(v["confidence"] for v in selection_votes)
            avg_confidence = (
                weighted_sum / len(selection_votes) if selection_votes else 0.0
            )
            results[selection] = {
                "weighted_score": weighted_sum,
                "avg_confidence": avg_confidence,
                "vote_count": len(selection_votes),
            }

        winner = max(results.keys(), key=lambda s: results[s]["weighted_score"])

        return {
            "status": "complete",
            "result": winner,
            "details": results,
            "consensus_strength": (
                results[winner]["weighted_score"] / len(votes) if votes else 0.0
            ),
        }


# ---------------------------------------------------------------------------
# Failure Handling
# ---------------------------------------------------------------------------


class AgentFailureHandler:
    """Handler for agent failures in multi-agent systems.

    Use when: agents may fail and the system needs retry logic with
    exponential backoff, circuit breakers, and automatic rerouting to
    backup agents.
    """

    def __init__(
        self,
        communication: AgentCommunication,
        max_retries: int = 3,
    ) -> None:
        self.communication = communication
        self.max_retries = max_retries
        self.failure_counts: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, float] = {}  # agent -> unlock time

    def handle_failure(
        self, agent_id: str, task_id: str, error: str
    ) -> Dict[str, Any]:
        """Handle a failure from an agent.

        Use when: an agent reports an error and the system must decide
        whether to retry (with backoff) or reroute to a backup agent.
        """
        self.failure_counts[agent_id] = (
            self.failure_counts.get(agent_id, 0) + 1
        )

        if self.failure_counts[agent_id] >= self.max_retries:
            self._activate_circuit_breaker(agent_id)
            return {
                "action": "reroute",
                "reason": "circuit_breaker_activated",
                "alternative": self._find_alternative_agent(agent_id),
            }

        return {
            "action": "retry",
            "reason": error,
            "retry_count": self.failure_counts[agent_id],
            "delay": min(2 ** self.failure_counts[agent_id], 60),
        }

    def _activate_circuit_breaker(self, agent_id: str) -> None:
        """Temporarily disable an agent (1-minute cooldown)."""
        self.circuit_breakers[agent_id] = time.time() + 60

    def _find_alternative_agent(self, failed_agent: str) -> str:
        """Find an alternative agent to handle the task.

        In production, check agent capabilities and availability.
        """
        return "default_backup_agent"

    def is_available(self, agent_id: str) -> bool:
        """Check if an agent is available (circuit breaker not active)."""
        if agent_id in self.circuit_breakers:
            if time.time() < self.circuit_breakers[agent_id]:
                return False
            del self.circuit_breakers[agent_id]
            self.failure_counts[agent_id] = 0
        return True

    def record_success(self, agent_id: str) -> None:
        """Record a successful task completion, resetting failure count."""
        self.failure_counts[agent_id] = 0


# ---------------------------------------------------------------------------
# Demo / CLI entry point
# ---------------------------------------------------------------------------


# CLI
# ---------------------------------------------------------------------------


def run_scenario(workers: int, failures: int, max_retries: int,
                 voters: int) -> Dict[str, Any]:
    """Exercise every coordination primitive once and return what happened.

    Deterministic: no randomness, no clock-dependent branching, so the same
    arguments always produce the same result and this is usable as a fixture.
    """
    comm = AgentCommunication()

    supervisor = SupervisorAgent("supervisor", comm)
    worker_names = [f"worker_{i}" for i in range(workers)]
    for name in worker_names:
        supervisor.register_worker(name, ["search", "analyze"])

    protocol = HandoffProtocol(comm)
    handoff_accepted = False
    if len(worker_names) >= 2:
        comm.send(protocol.create_handoff(
            from_agent=worker_names[0],
            to_agent=worker_names[1],
            context={"findings": ["item1", "item2"]},
            reason="stage_complete",
        ))
        handoff_accepted = bool(protocol.accept_handoff(worker_names[1]))

    consensus = ConsensusManager()
    voter_names = [f"voter_{i}" for i in range(voters)]
    consensus.initiate_vote("best_approach", voter_names, ["A", "B"])
    # Alternate A/B with descending confidence so the outcome is fixed and the
    # weighting is visible rather than incidental.
    for i, voter in enumerate(voter_names):
        consensus.submit_vote("best_approach", voter,
                              "A" if i % 2 == 0 else "B",
                              confidence=0.9 - (i * 0.1))
    vote = consensus.calculate_weighted_consensus("best_approach")

    handler = AgentFailureHandler(comm, max_retries=max_retries)
    last_action: Dict[str, Any] = {}
    for _ in range(failures):
        last_action = handler.handle_failure("flaky_agent", "task_1", "timeout")

    return {
        "workers_registered": worker_names,
        "handoff_accepted": handoff_accepted,
        "consensus": {
            "result": vote["result"],
            "strength": round(vote["consensus_strength"], 4),
            "voters": len(voter_names),
        },
        "failure_handling": {
            "failures_injected": failures,
            "max_retries": max_retries,
            "final_action": last_action.get("action"),
            "agent_still_available": handler.is_available("flaky_agent"),
        },
    }


def format_scenario(out: Dict[str, Any]) -> str:
    """Render a scenario result as plain text."""
    fh = out["failure_handling"]
    return "\n".join([
        f"Workers registered: {', '.join(out['workers_registered']) or '(none)'}",
        f"Handoff accepted:   {out['handoff_accepted']}",
        f"Consensus:          {out['consensus']['result']} "
        f"(strength {out['consensus']['strength']:.2f} "
        f"across {out['consensus']['voters']} voters)",
        f"Failure handling:   {fh['failures_injected']} failures, "
        f"max_retries={fh['max_retries']} -> action={fh['final_action']}",
        f"Agent available:    {fh['agent_still_available']}",
    ])


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="coordination.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Exercise the multi-agent coordination primitives: supervisor "
            "registration, handoff protocol, weighted consensus, and failure "
            "handling with retry budgets.\n"
            "Segment 2 of agent-oracle. Import the classes to build a real "
            "topology; run this to see how the pieces behave together."
        ),
        epilog="""
Examples:
  python3 coordination.py                          default scenario, text output
  python3 coordination.py --json                   the same run as JSON
  python3 coordination.py --workers 5 --voters 5   a wider fan-out
  python3 coordination.py --failures 5 --max-retries 2   force a reroute

Exit codes:
  0  scenario ran
  1  bad arguments
        """,
    )
    parser.add_argument("--workers", type=int, default=2, metavar="N",
                        help="workers to register under the supervisor (default: 2)")
    parser.add_argument("--voters", type=int, default=3, metavar="N",
                        help="agents participating in the consensus vote (default: 3)")
    parser.add_argument("--failures", type=int, default=3, metavar="N",
                        help="consecutive failures to inject (default: 3)")
    parser.add_argument("--max-retries", type=int, default=3, metavar="N",
                        help="retry budget before the agent is taken out (default: 3)")
    parser.add_argument("--json", action="store_true",
                        help="emit the scenario result as JSON instead of text")
    args = parser.parse_args(argv)

    for name, value in (("--workers", args.workers), ("--voters", args.voters),
                        ("--failures", args.failures),
                        ("--max-retries", args.max_retries)):
        if value < 0:
            parser.error(f"{name} must be zero or greater")
    if args.voters < 1:
        parser.error("--voters must be at least 1; a vote needs a voter")

    out = run_scenario(args.workers, args.failures, args.max_retries, args.voters)
    print(json.dumps(out, indent=2, sort_keys=True) if args.json
          else format_scenario(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
