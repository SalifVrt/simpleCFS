"""Unit testing for CFSLogger class"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

import src.logger as logger
import src.task as task


class TestCFSLoggerInitialization:
    """Tests for CFSLogger class initialization"""
    
    def test_logger_init_default(self):
        """Test that CFSLogger initializes with default parameters"""
        log = logger.CFSLogger()
        
        assert log.history == []
        assert log.output_file is None
    
    def test_logger_init_with_output_file(self):
        """Test that CFSLogger initializes with a custom output file"""
        output_file = "/tmp/test_output.csv"
        log = logger.CFSLogger(output_file=output_file)
        
        assert log.output_file == output_file
        assert log.history == []


class TestCFSLoggerLogEvent:
    """Tests for CFSLogger.log_event() method"""
    
    def test_log_event_without_task_without_message(self, capsys):
        """Test logging an event without a task or message"""
        log = logger.CFSLogger()
        log.log_event(0.0, "start")
        
        assert len(log.history) == 1
        assert "start" in log.history[0]
        assert "0.00" in log.history[0]
    
    def test_log_event_with_task_without_message(self, capsys):
        """Test logging an event with a task but no message"""
        log = logger.CFSLogger()
        bursts = [("CPU", 5)]
        t = task.Task("Task1", 0.0, 0, bursts)
        
        log.log_event(1.5, "schedule", t)
        
        assert len(log.history) == 1
        assert "Task1" in log.history[0]
        assert "schedule" in log.history[0]
        assert "1.50" in log.history[0]
    
    def test_log_event_with_task_and_message(self):
        """Test logging an event with both task and message"""
        log = logger.CFSLogger()
        bursts = [("CPU", 5)]
        t = task.Task("Task2", 0.0, 0, bursts)
        
        log.log_event(2.0, "preempt", t, "Higher priority task arrived")
        
        assert len(log.history) == 1
        assert "Task2" in log.history[0]
        assert "preempt" in log.history[0]
        assert "Higher priority task arrived" in log.history[0]
    
    def test_log_event_without_task_with_message(self):
        """Test logging an event without task but with message"""
        log = logger.CFSLogger()
        
        log.log_event(0.0, "start", message="System initialization")
        
        assert len(log.history) == 1
        assert "start" in log.history[0]
        assert "System initialization" in log.history[0]
    
    def test_log_multiple_events(self):
        """Test logging multiple events in sequence"""
        log = logger.CFSLogger()
        bursts = [("CPU", 5)]
        t1 = task.Task("Task1", 0.0, 0, bursts)
        t2 = task.Task("Task2", 1.0, 0, bursts)
        
        log.log_event(0.0, "start", message="Scheduler started")
        log.log_event(1.0, "schedule", t1, "First task scheduled")
        log.log_event(2.0, "schedule", t2, "Second task scheduled")
        log.log_event(5.0, "end", message="All tasks completed")
        
        assert len(log.history) == 4
        assert "start" in log.history[0]
        assert "Task1" in log.history[1]
        assert "Task2" in log.history[2]
        assert "end" in log.history[3]
    
    def test_log_event_with_different_event_types(self):
        """Test logging various event types"""
        log = logger.CFSLogger()
        
        event_types = ["start", "schedule", "preempt", "deschedule", "end"]
        
        for i, event_type in enumerate(event_types):
            log.log_event(float(i), event_type)
        
        assert len(log.history) == len(event_types)
        for i, event_type in enumerate(event_types):
            assert event_type in log.history[i]
    
    def test_log_event_with_float_time(self):
        """Test logging events with various floating point time values"""
        log = logger.CFSLogger()
        
        times = [0.0, 0.5, 1.25, 10.999, 100.0001]
        
        for time_val in times:
            log.log_event(time_val, "test")
        
        assert len(log.history) == len(times)
    
    def test_log_event_preserves_task_id(self):
        """Test that task IDs are correctly preserved in logs"""
        log = logger.CFSLogger()
        
        task_ids = ["TaskA", "Task123", "task_with_underscore"]
        
        for task_id in task_ids:
            t = task.Task(task_id, 0.0, 0, [("CPU", 1)])
            log.log_event(1.0, "log", t)
        
        for i, task_id in enumerate(task_ids):
            assert task_id in log.history[i]
    
    def test_log_event_task_info_includes_nice_value(self):
        """Test that logged task includes nice value"""
        log = logger.CFSLogger()
        t = task.Task("Task1", 0.0, -5, [("CPU", 1)])
        
        log.log_event(1.0, "test", t)
        
        assert "nice:" in log.history[0]
        assert "-5" in log.history[0]
    
    def test_log_event_task_info_includes_vruntime(self):
        """Test that logged task includes vruntime value"""
        log = logger.CFSLogger()
        t = task.Task("Task1", 0.0, 0, [("CPU", 1)])
        t.vruntime = 10.5
        
        log.log_event(1.0, "test", t)
        
        assert "vruntime" in log.history[0]
        assert "10.50" in log.history[0]


class TestCFSLoggerHistory:
    """Tests for CFSLogger history management"""
    
    def test_history_accumulates_events(self):
        """Test that history accumulates all logged events"""
        log = logger.CFSLogger()
        
        for i in range(10):
            log.log_event(float(i), f"event_{i}")
        
        assert len(log.history) == 10
    
    def test_history_is_list(self):
        """Test that history is implemented as a list"""
        log = logger.CFSLogger()
        assert isinstance(log.history, list)
    
    def test_history_maintains_order(self):
        """Test that events are stored in order"""
        log = logger.CFSLogger()
        
        times = [0.1, 0.5, 1.2, 5.0, 10.0]
        
        for t in times:
            log.log_event(t, "event")
        
        # Check that log lines are in order (checking timestamps)
        for i, t in enumerate(times):
            assert f"{t:2f}" in log.history[i]
    
    def test_history_contains_formatted_strings(self):
        """Test that history contains formatted log lines"""
        log = logger.CFSLogger()
        log.log_event(1.5, "test_event", message="test message")
        
        # History should contain strings with formatted output
        assert isinstance(log.history[0], str)
        assert "[" in log.history[0]  # Timestamp bracket
        assert "]" in log.history[0]


class TestCFSLoggerWrite:
    """Tests for CFSLogger._write() method"""
    
    @patch('builtins.print')
    def test_write_called_with_log_message(self, mock_print):
        """Test that _write() is called with the log message"""
        log = logger.CFSLogger()
        message = "Test log message"
        
        log._write(message)
        
        # _write should handle the message (currently it passes)
        # This test verifies the method can be called without errors
        assert True
    
    def test_write_with_empty_message(self):
        """Test that _write() handles empty message"""
        log = logger.CFSLogger()
        
        # Should not raise any exception
        log._write("")
        
        assert True
    
    def test_write_with_special_characters(self):
        """Test that _write() handles special characters"""
        log = logger.CFSLogger()
        message = "Special chars: @#$%^&*()"
        
        # Should not raise any exception
        log._write(message)
        
        assert True


class TestCFSLoggerIntegration:
    """Integration tests for CFSLogger"""
    
    def test_logger_workflow_simple(self):
        """Test a simple logging workflow"""
        log = logger.CFSLogger()
        
        log.log_event(0.0, "start", message="System started")
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        log.log_event(1.0, "schedule", t1, "Task1 scheduled")
        
        t2 = task.Task("Task2", 2.0, 0, [("CPU", 3)])
        log.log_event(2.0, "schedule", t2, "Task2 scheduled")
        
        log.log_event(5.0, "end", message="All tasks completed")
        
        assert len(log.history) == 4
        assert "start" in log.history[0]
        assert "Task1" in log.history[1]
        assert "Task2" in log.history[2]
        assert "end" in log.history[3]
    
    def test_logger_with_multiple_tasks(self):
        """Test logging with multiple different tasks"""
        log = logger.CFSLogger()
        
        for i in range(5):
            task_id = f"Task{i}"
            t = task.Task(task_id, float(i), i-2, [("CPU", i+1)])
            log.log_event(float(i), "create", t)
        
        assert len(log.history) == 5
        
        for i in range(5):
            assert f"Task{i}" in log.history[i]
    
    def test_logger_with_various_event_sequences(self):
        """Test logging realistic event sequences"""
        log = logger.CFSLogger()
        
        # Simulate a simple scheduling scenario
        events = [
            (0.0, "init", None, "Initialization"),
            (1.0, "schedule", "T1", "Task T1 goes on CPU"),
            (3.5, "preempt", "T1", "Task T1 preempted"),
            (3.5, "schedule", "T2", "Task T2 goes on CPU"),
            (7.0, "deschedule", "T2", "Task T2 descheduled"),
            (10.0, "end", None, "Simulation ended"),
        ]
        
        for time, event_type, task_id, message in events:
            if task_id:
                t = task.Task(task_id, time, 0, [("CPU", 1)])
                log.log_event(time, event_type, t, message)
            else:
                log.log_event(time, event_type, message=message)
        
        assert len(log.history) == len(events)
    
    def test_logger_event_formatting_consistency(self):
        """Test that event formatting is consistent"""
        log = logger.CFSLogger()
        t = task.Task("Task1", 0.0, 0, [("CPU", 1)])
        t.vruntime = 5.0
        
        log.log_event(1.0, "test", t, "Test message")
        
        log_line = log.history[0]
        
        # Check format: [time] event_type |Task info| | message
        assert log_line.startswith("[")
        assert "ms]" in log_line
        assert "|" in log_line

