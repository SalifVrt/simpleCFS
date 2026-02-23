"""Unit testing for CFSLogger class"""
import pytest
import tempfile
import os
from unittest.mock import patch, mock_open

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
    
    def test_log_event_without_task(self, capsys):
        """Test logging an event without a task"""
        log = logger.CFSLogger()
        log.log_event(0.0, "start")
        
        assert len(log.history) == 1
        assert log.history[0] == [0.0, "start"]
        
        captured = capsys.readouterr()
        assert "time: 0.0, start" in captured.out
    
    def test_log_event_with_task(self, capsys):
        """Test logging an event with a task"""
        log = logger.CFSLogger()
        bursts = [("CPU", 5)]
        t = task.Task("Task1", 0.0, 0, bursts)
        
        log.log_event(1.5, "schedule", t)
        
        assert len(log.history) == 1
        assert log.history[0] == [1.5, "schedule", "Task1"]
        
        captured = capsys.readouterr()
        assert "time: 1.5, schedule of task Task1" in captured.out
    
    def test_log_multiple_events(self, capsys):
        """Test logging multiple events in sequence"""
        log = logger.CFSLogger()
        bursts = [("CPU", 5)]
        t1 = task.Task("Task1", 0.0, 0, bursts)
        t2 = task.Task("Task2", 1.0, 0, bursts)
        
        log.log_event(0.0, "start")
        log.log_event(1.0, "schedule", t1)
        log.log_event(2.0, "schedule", t2)
        log.log_event(5.0, "end")
        
        assert len(log.history) == 4
        assert log.history[0] == [0.0, "start"]
        assert log.history[1] == [1.0, "schedule", "Task1"]
        assert log.history[2] == [2.0, "schedule", "Task2"]
        assert log.history[3] == [5.0, "end"]
    
    def test_log_event_with_different_event_types(self):
        """Test logging various event types"""
        log = logger.CFSLogger()
        
        event_types = ["start", "schedule", "preempt", "deschedule", "end"]
        
        for i, event_type in enumerate(event_types):
            log.log_event(float(i), event_type)
        
        assert len(log.history) == len(event_types)
        for i, event_type in enumerate(event_types):
            assert log.history[i][1] == event_type
    
    def test_log_event_with_float_time(self):
        """Test logging events with various floating point time values"""
        log = logger.CFSLogger()
        
        times = [0.0, 0.5, 1.25, 10.999, 100.0001]
        
        for time_val in times:
            log.log_event(time_val, "test")
        
        assert len(log.history) == len(times)
        for i, time_val in enumerate(times):
            assert log.history[i][0] == time_val
    
    def test_log_event_preserves_task_id(self):
        """Test that task IDs are correctly preserved in logs"""
        log = logger.CFSLogger()
        
        task_ids = ["TaskA", "Task123", "task_with_underscore"]
        tasks = []
        
        for task_id in task_ids:
            t = task.Task(task_id, 0.0, 0, [("CPU", 1)])
            tasks.append(t)
            log.log_event(1.0, "log", t)
        
        for i, task_id in enumerate(task_ids):
            assert log.history[i][2] == task_id


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
        
        for i, t in enumerate(times):
            assert log.history[i][0] == t


class TestCFSLoggerWrite:
    """Tests for CFSLogger._write() method"""
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    @patch("time.ctime")
    def test_write_creates_file(self, mock_ctime, mock_csv_writer, mock_file):
        """Test that _write() creates a file with timestamp in name"""
        mock_ctime.return_value = "Mon Jan  1 00:00:00 2024"
        
        log = logger.CFSLogger()
        log.log_event(0.0, "start")
        log.log_event(1.0, "end")
        
        log._write()
        
        # Verify file was opened
        mock_file.assert_called_once()
        call_args = mock_file.call_args[0][0]
        assert "log_Mon Jan  1 00:00:00 2024" in call_args
        assert call_args.endswith(".csv") or "../logs/" in call_args
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    @patch("time.ctime")
    def test_write_exports_history(self, mock_ctime, mock_csv_writer, mock_file):
        """Test that _write() exports all history entries"""
        mock_ctime.return_value = "Test Time"
        mock_writer = mock_csv_writer.return_value
        
        log = logger.CFSLogger()
        log.log_event(0.0, "start")
        log.log_event(1.0, "event1")
        log.log_event(2.0, "event2")
        
        log._write()
        
        # Verify csv writer was called for each event
        assert mock_writer.writerow.call_count == 3
    
    @patch("builtins.open", new_callable=mock_open)
    @patch("csv.writer")
    @patch("time.ctime")
    def test_write_with_task_events(self, mock_ctime, mock_csv_writer, mock_file):
        """Test that _write() correctly exports events with tasks"""
        mock_ctime.return_value = "Test Time"
        mock_writer = mock_csv_writer.return_value
        
        log = logger.CFSLogger()
        t = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        
        log.log_event(0.0, "start")
        log.log_event(1.0, "schedule", t)
        
        log._write()
        
        # Check that writerow was called with the right data
        calls = mock_writer.writerow.call_args_list
        assert calls[0][0][0] == [0.0, "start"]
        assert calls[1][0][0] == [1.0, "schedule", "Task1"]


class TestCFSLoggerPrintSummary:
    """Tests for CFSLogger.print_summary() method"""
    
    def test_print_summary_basic(self, capsys):
        """Test that print_summary() produces output"""
        log = logger.CFSLogger()
        log.print_summary()
        
        captured = capsys.readouterr()
        assert "summary" in captured.out.lower()
    
    def test_print_summary_doesnt_crash_with_empty_history(self, capsys):
        """Test that print_summary() works with empty history"""
        log = logger.CFSLogger()
        
        # Should not raise any exception
        log.print_summary()
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_print_summary_doesnt_crash_with_populated_history(self, capsys):
        """Test that print_summary() works with populated history"""
        log = logger.CFSLogger()
        t = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        
        log.log_event(0.0, "start")
        log.log_event(1.0, "schedule", t)
        log.log_event(2.0, "end")
        
        # Should not raise any exception
        log.print_summary()
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestCFSLoggerIntegration:
    """Integration tests for CFSLogger"""
    
    def test_logger_workflow_simple(self, capsys):
        """Test a simple logging workflow"""
        log = logger.CFSLogger()
        
        log.log_event(0.0, "start")
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        log.log_event(1.0, "schedule", t1)
        
        t2 = task.Task("Task2", 2.0, 0, [("CPU", 3)])
        log.log_event(2.0, "schedule", t2)
        
        log.log_event(5.0, "end")
        
        assert len(log.history) == 4
        
        captured = capsys.readouterr()
        assert "start" in captured.out
        assert "Task1" in captured.out
        assert "Task2" in captured.out
        assert "end" in captured.out
    
    def test_logger_with_multiple_tasks(self):
        """Test logging with multiple different tasks"""
        log = logger.CFSLogger()
        
        tasks_dict = {}
        for i in range(5):
            task_id = f"Task{i}"
            t = task.Task(task_id, float(i), 0, [("CPU", i+1)])
            tasks_dict[task_id] = t
            log.log_event(float(i), "create", t)
        
        assert len(log.history) == 5
        
        for i in range(5):
            assert log.history[i][2] == f"Task{i}"
    
    def test_logger_with_various_event_sequences(self):
        """Test logging realistic event sequences"""
        log = logger.CFSLogger()
        
        # Simulate a simple scheduling scenario
        events = [
            (0.0, "init", None),
            (1.0, "schedule", "T1"),
            (3.5, "preempt", "T1"),
            (3.5, "schedule", "T2"),
            (7.0, "deschedule", "T2"),
            (10.0, "end", None),
        ]
        
        for time, event_type, task_id in events:
            if task_id:
                t = task.Task(task_id, time, 0, [("CPU", 1)])
                log.log_event(time, event_type, t)
            else:
                log.log_event(time, event_type)
        
        assert len(log.history) == len(events)
