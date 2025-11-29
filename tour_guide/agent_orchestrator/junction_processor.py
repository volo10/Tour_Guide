"""
Junction Processor with Threading.

Processes a single junction by spawning threads for each agent,
collecting results in a queue, and having the Judge decide.
"""

import logging
import threading
import queue
import time
from datetime import datetime
from typing import Optional, List, Callable

from ..route_fetcher.models import Junction
from .models import AgentResult, JunctionResults, AgentType
from .base_agent import BaseAgent
from .agents import VideoAgent, MusicAgent, HistoryAgent, JudgeAgent

logger = logging.getLogger(__name__)


class JunctionProcessor:
    """
    Processes a single junction using multiple agent threads.

    Architecture:
    - Main thread receives a junction
    - Spawns 3 sub-threads (one per contestant agent)
    - Each agent puts its result in a size-3 queue
    - When queue is full, Judge evaluates and picks winner
    """

    # Queue size = number of contestant agents
    QUEUE_SIZE = 3

    def __init__(
        self,
        video_agent: Optional[VideoAgent] = None,
        music_agent: Optional[MusicAgent] = None,
        history_agent: Optional[HistoryAgent] = None,
        judge_agent: Optional[JudgeAgent] = None,
        timeout_seconds: float = 30.0,
    ):
        """
        Initialize the junction processor.

        Args:
            video_agent: Video agent instance (created if None)
            music_agent: Music agent instance (created if None)
            history_agent: History agent instance (created if None)
            judge_agent: Judge agent instance (created if None)
            timeout_seconds: Max time to wait for agents
        """
        # Create agents if not provided
        self.video_agent = video_agent or VideoAgent()
        self.music_agent = music_agent or MusicAgent()
        self.history_agent = history_agent or HistoryAgent()
        self.judge_agent = judge_agent or JudgeAgent()

        # Initialize agents (loads API keys from config)
        self.video_agent.initialize()
        self.music_agent.initialize()
        self.history_agent.initialize()
        self.judge_agent.initialize()

        self.timeout = timeout_seconds

        # Results queue (size 3 for the 3 contestants)
        self._results_queue: queue.Queue = queue.Queue(maxsize=self.QUEUE_SIZE)

    def _agent_worker(
        self,
        agent: BaseAgent,
        junction: Junction,
        results_queue: queue.Queue,
    ):
        """
        Worker function that runs an agent in a thread.

        Args:
            agent: The agent to run
            junction: Junction to process
            results_queue: Queue to put result into
        """
        junction_id = junction.junction_id
        agent_type = agent.agent_type.value
        logger.debug(f"[JID-{junction_id}] {agent_type} agent thread started")

        try:
            result = agent.process_with_timing(junction)
            results_queue.put(result)
            logger.info(f"[JID-{junction_id}] {agent_type} completed: '{result.title}' "
                       f"(relevance: {result.relevance_score:.1f}, quality: {result.quality_score:.1f})")
        except Exception as e:
            logger.error(f"[JID-{junction_id}] {agent_type} agent error: {e}", exc_info=True)
            # Put error result
            error_result = AgentResult(
                agent_type=agent.agent_type,
                agent_name=agent.name,
                junction_id=junction.junction_id,
                junction_address=junction.address,
                title="",
                description="",
                error=str(e),
            )
            results_queue.put(error_result)

    def process(
        self,
        junction: Junction,
        junction_index: int = 0
    ) -> JunctionResults:
        """
        Process a junction with all agents.

        Spawns 3 threads for contestant agents, waits for all results
        in the queue, then has the Judge evaluate.

        Args:
            junction: The junction to process
            junction_index: Index of junction in route

        Returns:
            JunctionResults with all agent results and winner
        """
        junction_id = junction.junction_id
        start_time = datetime.now()
        start_timer = time.time()

        logger.info(f"[JID-{junction_id}] Processing junction: {junction.address}")

        # Create fresh queue for this junction
        self._results_queue = queue.Queue(maxsize=self.QUEUE_SIZE)

        # Create result container
        junction_results = JunctionResults(
            junction=junction,
            junction_index=junction_index,
            started_at=start_time,
        )

        # Spawn threads for each contestant agent
        threads: List[threading.Thread] = []

        agents = [
            (self.video_agent, "video"),
            (self.music_agent, "music"),
            (self.history_agent, "history"),
        ]

        logger.debug(f"[JID-{junction_id}] Spawning 3 agent threads (video, music, history)")

        for agent, name in agents:
            thread = threading.Thread(
                target=self._agent_worker,
                args=(agent, junction, self._results_queue),
                name=f"Agent-{name}-J{junction.junction_id}",
                daemon=True,
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete (with timeout)
        for thread in threads:
            remaining_timeout = max(0.1, self.timeout - (time.time() - start_timer))
            thread.join(timeout=remaining_timeout)

        # Collect results from queue
        collected_results: List[AgentResult] = []

        try:
            while not self._results_queue.empty():
                result = self._results_queue.get_nowait()
                collected_results.append(result)

                # Assign to appropriate slot
                if result.agent_type == AgentType.VIDEO:
                    junction_results.video_result = result
                elif result.agent_type == AgentType.MUSIC:
                    junction_results.music_result = result
                elif result.agent_type == AgentType.HISTORY:
                    junction_results.history_result = result

        except queue.Empty:
            pass

        # Check for missing results (timeout)
        expected_agents = {AgentType.VIDEO, AgentType.MUSIC, AgentType.HISTORY}
        received_agents = {r.agent_type for r in collected_results}
        missing_agents = expected_agents - received_agents

        for missing in missing_agents:
            error_msg = f"{missing.value} agent timed out"
            junction_results.errors.append(error_msg)
            logger.warning(f"[JID-{junction_id}] {error_msg}")

        logger.info(f"[JID-{junction_id}] Collected {len(collected_results)}/3 agent results")

        # Have the Judge evaluate (if we have any results)
        if collected_results:
            try:
                logger.debug(f"[JID-{junction_id}] Judge evaluating {len(collected_results)} results")
                decision = self.judge_agent.evaluate(junction, collected_results)
                junction_results.decision = decision
                junction_results.is_complete = True
                logger.info(f"[JID-{junction_id}] Judge selected: {decision.winner_type.value}")
            except Exception as e:
                error_msg = f"Judge error: {e}"
                junction_results.errors.append(error_msg)
                logger.error(f"[JID-{junction_id}] {error_msg}", exc_info=True)
        else:
            error_msg = "No agent results to evaluate"
            junction_results.errors.append(error_msg)
            logger.error(f"[JID-{junction_id}] {error_msg}")

        # Finalize timing
        junction_results.completed_at = datetime.now()
        junction_results.total_processing_time_ms = (time.time() - start_timer) * 1000

        logger.info(f"[JID-{junction_id}] Processing complete in {junction_results.total_processing_time_ms:.1f}ms")

        return junction_results

    def process_async(
        self,
        junction: Junction,
        junction_index: int,
        callback: Callable[[JunctionResults], None],
    ) -> threading.Thread:
        """
        Process a junction asynchronously.

        Runs processing in a separate thread and calls callback when done.

        Args:
            junction: The junction to process
            junction_index: Index of junction in route
            callback: Function to call with JunctionResults

        Returns:
            The thread handling the processing
        """
        def worker():
            result = self.process(junction, junction_index)
            callback(result)

        thread = threading.Thread(
            target=worker,
            name=f"JunctionProcessor-J{junction.junction_id}",
            daemon=True,
        )
        thread.start()
        return thread


class ThreadedJunctionProcessor(JunctionProcessor):
    """
    Extended processor that handles multiple junctions concurrently.

    Each junction gets its own processing thread, which in turn
    spawns sub-threads for each agent.
    """

    def __init__(
        self,
        max_concurrent_junctions: int = 3,
        **kwargs
    ):
        """
        Initialize the threaded processor.

        Args:
            max_concurrent_junctions: Max junctions to process at once
            **kwargs: Passed to JunctionProcessor
        """
        super().__init__(**kwargs)
        self.max_concurrent = max_concurrent_junctions
        self._active_threads: List[threading.Thread] = []
        self._results_lock = threading.Lock()
        self._all_results: List[JunctionResults] = []

    def process_batch(
        self,
        junctions: List[Junction],
        on_complete: Optional[callable] = None,
    ) -> List[JunctionResults]:
        """
        Process multiple junctions with controlled concurrency.

        Args:
            junctions: List of junctions to process
            on_complete: Optional callback for each completed junction

        Returns:
            List of JunctionResults in order
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = [None] * len(junctions)  # Preserve order

        def process_one(index: int, junction: Junction) -> tuple:
            result = self.process(junction, index)
            if on_complete:
                on_complete(result)
            return (index, result)

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            futures = {
                executor.submit(process_one, i, j): i
                for i, j in enumerate(junctions)
            }

            for future in as_completed(futures):
                index, result = future.result()
                results[index] = result

        return results
