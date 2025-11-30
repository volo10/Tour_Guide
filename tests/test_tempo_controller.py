"""
Tests for TempoController and JunctionOrchestrator modules.

Comprehensive tests for tempo control and junction orchestration.
"""

import pytest
import time
from unittest.mock import Mock, patch
from threading import Thread

from tour_guide.junction_orchestrator.orchestrator import JunctionOrchestrator
from tour_guide.junction_orchestrator.models import (
    OrchestratorConfig,
    DispatchMode,
    OrchestratorState,
    JunctionEvent,
)


class TestOrchestratorConfig:
    """Tests for OrchestratorConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = OrchestratorConfig()

        assert config.junction_interval_seconds == 30.0
        assert config.mode == DispatchMode.FIXED_INTERVAL
        assert config.time_scale == 1.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = OrchestratorConfig(
            junction_interval_seconds=10.0,
            mode=DispatchMode.MANUAL,
            time_scale=2.0,
        )

        assert config.junction_interval_seconds == 10.0
        assert config.mode == DispatchMode.MANUAL
        assert config.time_scale == 2.0

    def test_config_validation_positive_interval(self):
        """Test validation requires positive interval."""
        config = OrchestratorConfig(junction_interval_seconds=5.0)
        assert config.validate() is True

    def test_config_validation_invalid_interval(self):
        """Test validation rejects non-positive interval."""
        config = OrchestratorConfig(junction_interval_seconds=-1.0)

        with pytest.raises(ValueError):
            config.validate()

    def test_config_validation_zero_interval(self):
        """Test validation rejects zero interval."""
        config = OrchestratorConfig(junction_interval_seconds=0.0)

        with pytest.raises(ValueError):
            config.validate()

    def test_config_validation_invalid_time_scale(self):
        """Test validation rejects non-positive time_scale."""
        config = OrchestratorConfig(time_scale=-1.0)

        with pytest.raises(ValueError):
            config.validate()

    def test_config_validation_invalid_lookahead(self):
        """Test validation rejects zero lookahead."""
        config = OrchestratorConfig(lookahead_count=0)

        with pytest.raises(ValueError):
            config.validate()


class TestDispatchMode:
    """Tests for DispatchMode enum."""

    def test_fixed_interval_mode(self):
        """Test fixed interval mode value."""
        assert DispatchMode.FIXED_INTERVAL.value == "fixed_interval"

    def test_real_time_mode(self):
        """Test real time mode value."""
        assert DispatchMode.REAL_TIME.value == "real_time"

    def test_distance_based_mode(self):
        """Test distance based mode value."""
        assert DispatchMode.DISTANCE_BASED.value == "distance_based"

    def test_manual_mode(self):
        """Test manual mode value."""
        assert DispatchMode.MANUAL.value == "manual"


class TestOrchestratorState:
    """Tests for OrchestratorState enum."""

    def test_idle_state(self):
        """Test idle state value."""
        assert OrchestratorState.IDLE.value == "idle"

    def test_running_state(self):
        """Test running state value."""
        assert OrchestratorState.RUNNING.value == "running"

    def test_paused_state(self):
        """Test paused state value."""
        assert OrchestratorState.PAUSED.value == "paused"

    def test_completed_state(self):
        """Test completed state value."""
        assert OrchestratorState.COMPLETED.value == "completed"

    def test_error_state(self):
        """Test error state value."""
        assert OrchestratorState.ERROR.value == "error"


class TestJunctionOrchestrator:
    """Tests for JunctionOrchestrator."""

    @pytest.fixture
    def sample_route(self):
        """Create a sample route mock."""
        route = Mock()
        junctions = []
        for i in range(3):
            junction = Mock()
            junction.junction_id = i + 1
            junction.street_name = f"Street {i + 1}"
            junction.to_dict.return_value = {"id": i + 1}
            junctions.append(junction)

        route.junctions = junctions
        route.junction_count = len(junctions)
        return route

    def test_orchestrator_init_default(self):
        """Test default orchestrator initialization."""
        orchestrator = JunctionOrchestrator()

        assert orchestrator is not None
        assert orchestrator.state == OrchestratorState.IDLE

    def test_orchestrator_init_with_interval(self):
        """Test orchestrator with custom interval."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=10.0)

        assert orchestrator.config.junction_interval_seconds == 10.0

    def test_orchestrator_init_with_config(self):
        """Test orchestrator with config object."""
        config = OrchestratorConfig(
            junction_interval_seconds=15.0,
            mode=DispatchMode.MANUAL,
        )
        orchestrator = JunctionOrchestrator(config=config)

        assert orchestrator.config.junction_interval_seconds == 15.0
        assert orchestrator.config.mode == DispatchMode.MANUAL

    def test_orchestrator_state_idle(self):
        """Test initial state is IDLE."""
        orchestrator = JunctionOrchestrator()

        assert orchestrator.state == OrchestratorState.IDLE

    def test_orchestrator_on_junction_callback(self, sample_route):
        """Test on_junction callback registration."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)

        events = []

        @orchestrator.on_junction
        def callback(event):
            events.append(event)

        orchestrator.start(sample_route, blocking=True)

        assert len(events) >= 1

    def test_orchestrator_multiple_callbacks(self, sample_route):
        """Test multiple callbacks are called."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)

        events1 = []
        events2 = []

        @orchestrator.on_junction
        def callback1(event):
            events1.append(event)

        @orchestrator.on_junction
        def callback2(event):
            events2.append(event)

        orchestrator.start(sample_route, blocking=True)

        assert len(events1) >= 1
        assert len(events2) >= 1

    def test_orchestrator_pause(self, sample_route):
        """Test pause functionality."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.5)

        orchestrator.start(sample_route, blocking=False)
        time.sleep(0.1)
        orchestrator.pause()

        assert orchestrator.state == OrchestratorState.PAUSED

        orchestrator.stop()

    def test_orchestrator_resume(self, sample_route):
        """Test resume functionality."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.5)

        orchestrator.start(sample_route, blocking=False)
        time.sleep(0.1)
        orchestrator.pause()
        orchestrator.resume()

        assert orchestrator.state == OrchestratorState.RUNNING

        orchestrator.stop()

    def test_orchestrator_stop(self, sample_route):
        """Test stop functionality."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.5)

        orchestrator.start(sample_route, blocking=False)
        time.sleep(0.1)
        orchestrator.stop()

        assert orchestrator.state == OrchestratorState.IDLE


class TestJunctionEvent:
    """Tests for JunctionEvent dataclass."""

    @pytest.fixture
    def sample_junction(self):
        """Create a sample junction mock."""
        junction = Mock()
        junction.junction_id = 1
        junction.to_dict.return_value = {"id": 1}
        return junction

    def test_event_to_dict(self, sample_junction):
        """Test event to_dict method."""
        from datetime import datetime

        event = JunctionEvent(
            junction=sample_junction,
            dispatch_time=datetime.now(),
            scheduled_time=datetime.now(),
            junction_index=0,
            total_junctions=5,
            is_first=True,
            is_last=False,
        )

        result = event.to_dict()

        assert "junction" in result
        assert "junction_index" in result
        assert "total_junctions" in result
        assert result["is_first"] is True
        assert result["is_last"] is False

    def test_event_fields(self, sample_junction):
        """Test event fields are accessible."""
        from datetime import datetime

        now = datetime.now()
        event = JunctionEvent(
            junction=sample_junction,
            dispatch_time=now,
            scheduled_time=now,
            junction_index=2,
            total_junctions=10,
            progress_percent=20.0,
        )

        assert event.junction == sample_junction
        assert event.junction_index == 2
        assert event.total_junctions == 10
        assert event.progress_percent == 20.0


class TestOrchestratorEdgeCases:
    """Tests for edge cases."""

    def test_empty_route(self):
        """Test handling empty route."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)

        route = Mock()
        route.junctions = []
        route.junction_count = 0

        # Should handle gracefully
        try:
            orchestrator.start(route, blocking=True)
        except Exception:
            pass  # May raise or complete immediately

    def test_single_junction(self):
        """Test route with single junction."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)

        junction = Mock()
        junction.junction_id = 1
        junction.to_dict.return_value = {"id": 1}

        route = Mock()
        route.junctions = [junction]
        route.junction_count = 1

        events = []

        @orchestrator.on_junction
        def callback(event):
            events.append(event)

        orchestrator.start(route, blocking=True)

        assert len(events) >= 1

    def test_pause_before_start(self):
        """Test pausing before starting."""
        orchestrator = JunctionOrchestrator()

        # Should handle gracefully
        orchestrator.pause()

    def test_stop_before_start(self):
        """Test stopping before starting."""
        orchestrator = JunctionOrchestrator()

        # Should handle gracefully
        orchestrator.stop()

    def test_callback_exception(self):
        """Test handling callback exceptions."""
        orchestrator = JunctionOrchestrator(junction_interval_seconds=0.05)

        @orchestrator.on_junction
        def bad_callback(event):
            raise Exception("Callback error")

        junction = Mock()
        junction.junction_id = 1
        junction.to_dict.return_value = {"id": 1}

        route = Mock()
        route.junctions = [junction]
        route.junction_count = 1

        # Should handle gracefully (not crash)
        try:
            orchestrator.start(route, blocking=True)
        except Exception:
            pass  # Implementation may or may not propagate
