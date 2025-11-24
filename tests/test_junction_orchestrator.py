"""
Unit tests for the junction_orchestrator module.
"""

import pytest
import time
from datetime import datetime

from tour_guide.junction_orchestrator.models import (
    OrchestratorConfig, JunctionEvent, OrchestratorState, DispatchMode
)
from tour_guide.junction_orchestrator.orchestrator import JunctionOrchestrator


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OrchestratorConfig()
        assert config.junction_interval_seconds == 30.0
        assert config.mode == DispatchMode.FIXED_INTERVAL
        assert config.time_scale == 1.0
        assert config.pre_dispatch_seconds == 5.0

    def test_custom_config(self):
        """Test custom configuration."""
        config = OrchestratorConfig(
            junction_interval_seconds=10.0,
            mode=DispatchMode.REAL_TIME,
            time_scale=2.0,
        )
        assert config.junction_interval_seconds == 10.0
        assert config.mode == DispatchMode.REAL_TIME
        assert config.time_scale == 2.0


class TestDispatchMode:
    """Tests for DispatchMode enum."""

    def test_all_modes_exist(self):
        """Test that all dispatch modes exist."""
        assert DispatchMode.FIXED_INTERVAL is not None
        assert DispatchMode.REAL_TIME is not None
        assert DispatchMode.MANUAL is not None


class TestOrchestratorState:
    """Tests for OrchestratorState enum."""

    def test_all_states_exist(self):
        """Test that all states exist."""
        assert OrchestratorState.IDLE is not None
        assert OrchestratorState.RUNNING is not None
        assert OrchestratorState.PAUSED is not None
        assert OrchestratorState.COMPLETED is not None


class TestJunctionEvent:
    """Tests for JunctionEvent dataclass."""

    def test_event_creation(self, sample_junction, sample_route):
        """Test creating a junction event."""
        now = datetime.now()
        event = JunctionEvent(
            junction=sample_junction,
            dispatch_time=now,
            scheduled_time=now,
            junction_index=0,
            total_junctions=4,
        )
        assert event.junction == sample_junction
        assert event.junction_index == 0
        assert event.total_junctions == 4

    def test_event_default_values(self, sample_junction):
        """Test event default values."""
        now = datetime.now()
        event = JunctionEvent(
            junction=sample_junction,
            dispatch_time=now,
            scheduled_time=now,
            junction_index=0,
            total_junctions=1,
        )
        assert event.delay_seconds == 0.0
        assert event.is_first is False
        assert event.is_last is False
        assert event.progress_percent == 0.0


class TestJunctionOrchestrator:
    """Tests for JunctionOrchestrator."""

    def test_orchestrator_creation(self):
        """Test creating an orchestrator."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=5.0)
        assert orchestrator.interval == 5.0

    def test_orchestrator_default_interval(self):
        """Test default interval."""
        orchestrator = JunctionOrchestrator()
        assert orchestrator.interval == 30.0

    def test_register_callback(self):
        """Test registering a callback."""
        orchestrator = JunctionOrchestrator()
        callback = lambda event: None
        orchestrator.register_callback(callback)
        assert callback in orchestrator._callbacks

    def test_on_junction_decorator(self):
        """Test the @on_junction decorator."""
        orchestrator = JunctionOrchestrator()

        @orchestrator.on_junction
        def handler(event):
            pass

        assert handler in orchestrator._callbacks

    def test_start_dispatches_events(self, sample_route):
        """Test that start dispatches junction events."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.1)
        received_events = []

        @orchestrator.on_junction
        def handler(event):
            received_events.append(event)

        orchestrator.start(sample_route, blocking=True)

        assert len(received_events) == sample_route.junction_count

    def test_event_has_correct_indices(self, sample_route):
        """Test that events have correct indices."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)
        received_events = []

        @orchestrator.on_junction
        def handler(event):
            received_events.append(event)

        orchestrator.start(sample_route, blocking=True)

        for i, event in enumerate(received_events):
            assert event.junction_index == i
            assert event.total_junctions == sample_route.junction_count

    def test_first_and_last_flags(self, sample_route):
        """Test is_first and is_last flags."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)
        received_events = []

        @orchestrator.on_junction
        def handler(event):
            received_events.append(event)

        orchestrator.start(sample_route, blocking=True)

        assert received_events[0].is_first is True
        assert received_events[0].is_last is False
        assert received_events[-1].is_first is False
        assert received_events[-1].is_last is True

    def test_stop_interrupts_dispatch(self, sample_route):
        """Test that stop interrupts the dispatch loop."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=1.0)
        received_events = []

        @orchestrator.on_junction
        def handler(event):
            received_events.append(event)
            if len(received_events) >= 2:
                orchestrator.stop()

        orchestrator.start(sample_route, blocking=True)

        # Should have stopped before processing all junctions
        assert len(received_events) <= 2

    def test_state_transitions(self, sample_route):
        """Test state transitions during orchestration."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)

        assert orchestrator.state == OrchestratorState.IDLE

        orchestrator.start(sample_route, blocking=True)

        assert orchestrator.state == OrchestratorState.COMPLETED

    def test_non_blocking_start(self, sample_route):
        """Test non-blocking start mode."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)
        received_events = []

        @orchestrator.on_junction
        def handler(event):
            received_events.append(event)

        orchestrator.start(sample_route, blocking=False)

        # Give time for async processing
        time.sleep(0.5)

        assert len(received_events) == sample_route.junction_count
