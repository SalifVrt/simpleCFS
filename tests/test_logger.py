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
    
    def test_write_to_console_when_no_output_file(self, capsys):
        """Test that _write() prints to console when output_file is None"""
        log = logger.CFSLogger()
        message = "Test log message"
        
        log._write(message)
        
        captured = capsys.readouterr()
        assert message in captured.out
    
    def test_write_multiple_messages_to_console(self, capsys):
        """Test that multiple _write() calls print to console"""
        log = logger.CFSLogger()
        messages = ["Message 1", "Message 2", "Message 3"]
        
        for msg in messages:
            log._write(msg)
        
        captured = capsys.readouterr()
        for msg in messages:
            assert msg in captured.out
    
    def test_write_to_file_when_output_file_set(self, tmp_path):
        """Test that _write() writes to file when output_file is set"""
        output_file = tmp_path / "test_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        message = "Test message to file"
        log._write(message)
        
        # Read the file and verify content
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert message in content
        assert "\n" in content  # Should have newline
    
    def test_write_appends_to_file(self, tmp_path):
        """Test that _write() appends to file instead of overwriting"""
        output_file = tmp_path / "test_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        messages = ["First message", "Second message", "Third message"]
        
        for msg in messages:
            log._write(msg)
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        # All messages should be present
        for msg in messages:
            assert msg in content
        
        # Count occurrences
        lines = content.strip().split('\n')
        assert len(lines) == 3
    
    def test_write_adds_newline(self, tmp_path):
        """Test that _write() adds newline to each message"""
        output_file = tmp_path / "test_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        log._write("Message 1")
        log._write("Message 2")
        
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        # Each message should have newline
        assert len(lines) == 2
        assert lines[0].endswith("\n")
        assert lines[1].endswith("\n")
    
    def test_write_with_empty_message_to_console(self, capsys):
        """Test that _write() handles empty message"""
        log = logger.CFSLogger()
        log._write("")
        
        captured = capsys.readouterr()
        # Should print just a newline
        assert captured.out == "\n"
    
    def test_write_with_special_characters(self, tmp_path):
        """Test that _write() preserves special characters"""
        output_file = tmp_path / "test_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        message = "Special chars: @#$%^&*()_+-=[]{}|;:,.<>?"
        log._write(message)
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert message in content
    
    def test_write_with_unicode_characters(self, tmp_path):
        """Test that _write() handles unicode characters"""
        output_file = tmp_path / "test_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        message = "Unicode test: ñ é ü 中文 🎉"
        log._write(message)
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert message in content
    
    def test_write_creates_file_if_not_exists(self, tmp_path):
        """Test that _write() creates output file if it doesn't exist"""
        output_file = tmp_path / "new_log.txt"
        
        # File should not exist yet
        assert not output_file.exists()
        
        log = logger.CFSLogger(output_file=str(output_file))
        log._write("Creating file")
        
        # File should now exist
        assert output_file.exists()
    
    def test_write_console_vs_file_behavior(self, capsys, tmp_path):
        """Test different behavior between console and file output"""
        # Console output
        console_log = logger.CFSLogger()
        console_log._write("Console message")
        captured = capsys.readouterr()
        assert "Console message" in captured.out
        
        # File output
        output_file = tmp_path / "file_log.txt"
        file_log = logger.CFSLogger(output_file=str(output_file))
        file_log._write("File message")
        captured = capsys.readouterr()
        assert "File message" not in captured.out
        
        with open(output_file, 'r') as f:
            assert "File message" in f.read()


class TestCFSLoggerPrintSummary:
    """Tests for CFSLogger.print_summary() method"""
    
    def test_print_summary_with_empty_tasks(self, capsys):
        """Test print_summary() with empty task list"""
        log = logger.CFSLogger()
        
        log.print_summary([])
        
        captured = capsys.readouterr()
        assert "SIMULATION FINISHED" in captured.out or "No task to show" in captured.out
    
    def test_print_summary_with_single_task(self, capsys):
        """Test print_summary() with single task"""
        log = logger.CFSLogger()
        tasks = [task.Task("Task1", 0.0, 0, [("CPU", 5)])]
        
        log.print_summary(tasks)
        
        captured = capsys.readouterr()
        assert "SIMULATION FINISHED" in captured.out or "STATS" in captured.out
    
    def test_print_summary_with_multiple_tasks(self, capsys):
        """Test print_summary() with multiple tasks"""
        log = logger.CFSLogger()
        tasks = [
            task.Task("Task1", 0.0, 0, [("CPU", 5)]),
            task.Task("Task2", 1.0, -2, [("CPU", 3)]),
            task.Task("Task3", 2.0, 2, [("CPU", 4)])
        ]
        
        log.print_summary(tasks)
        
        captured = capsys.readouterr()
        output = captured.out
        assert "SIMULATION FINISHED" in output or "STATS" in output
        assert "=" in output  # Should have separator line
    
    def test_print_summary_writes_separator(self, capsys):
        """Test that print_summary() includes separator"""
        log = logger.CFSLogger()
        tasks = []
        
        log.print_summary(tasks)
        
        captured = capsys.readouterr()
        # Should have at least one line with '=' characters
        assert "=" in captured.out
    
    def test_print_summary_includes_header(self, capsys):
        """Test that print_summary() includes header text"""
        log = logger.CFSLogger()
        tasks = []
        
        log.print_summary(tasks)
        
        captured = capsys.readouterr()
        output = captured.out.upper()
        assert "SIMULATION" in output or "STATS" in output
    
    def test_print_summary_to_file(self, tmp_path):
        """Test that print_summary() writes to file when configured"""
        output_file = tmp_path / "summary_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        tasks = [task.Task("Task1", 0.0, 0, [("CPU", 1)])]
        
        log.print_summary(tasks)
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert "SIMULATION FINISHED" in content or "STATS" in content
    
    def test_print_summary_to_console(self, capsys):
        """Test that print_summary() prints to console when no file"""
        log = logger.CFSLogger()
        tasks = [task.Task("T1", 0.0, 0, [("CPU", 1)])]
        
        log.print_summary(tasks)
        
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert "=" in captured.out
    
    def test_print_summary_formatting(self, capsys):
        """Test that print_summary() has consistent formatting"""
        log = logger.CFSLogger()
        tasks = []
        
        log.print_summary(tasks)
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        
        # Should have at least 3 lines (separator, header, separator)
        assert len(lines) >= 3
    
    def test_print_summary_preserves_task_list(self):
        """Test that print_summary() doesn't modify input task list"""
        log = logger.CFSLogger()
        tasks = [
            task.Task("Task1", 0.0, 0, [("CPU", 5)]),
            task.Task("Task2", 1.0, 0, [("CPU", 3)])
        ]
        original_len = len(tasks)
        
        log.print_summary(tasks)
        
        assert len(tasks) == original_len


class TestCFSLoggerIntegrationWrite:
    """Integration tests for _write() and print_summary() together"""
    
    def test_log_event_and_summary_to_file(self, tmp_path):
        """Test logging events and then printing summary to file"""
        output_file = tmp_path / "full_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        log.log_event(0.0, "start", message="Starting simulation")
        log.log_event(1.0, "schedule", t1, "Task1 scheduled")
        
        tasks = [t1]
        log.print_summary(tasks)
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert "start" in content
        assert "schedule" in content
        assert "SIMULATION FINISHED" in content or "STATS" in content
    
    def test_multiple_write_calls_maintain_order(self, tmp_path):
        """Test that multiple _write() calls maintain order in file"""
        output_file = tmp_path / "ordered_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        messages = [f"Line {i}" for i in range(10)]
        
        for msg in messages:
            log._write(msg)
        
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        # Verify order
        for i, expected in enumerate(messages):
            assert expected in lines[i]
    
    def test_write_and_print_summary_interaction(self, capsys):
        """Test interaction between _write() and print_summary()"""
        log = logger.CFSLogger()
        
        log._write("Initial message")
        t = task.Task("T1", 0.0, 0, [("CPU", 1)])
        log.print_summary([t])
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "Initial message" in output
        assert "SIMULATION" in output or "STATS" in output
        assert "=" in output


class TestCFSLoggerRecordGanttEntry:
    """Tests for CFSLogger.record_gantt_entry() method"""
    
    def test_record_gantt_entry_single_entry(self):
        """Test recording a single gantt entry"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("Task1", 0.0, 5.0)
        
        assert len(log.gantt_data) == 1
        assert log.gantt_data[0] == ("Task1", 0.0, 5.0)
    
    def test_record_gantt_entry_multiple_entries(self):
        """Test recording multiple gantt entries"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("Task1", 0.0, 5.0)
        log.record_gantt_entry("Task2", 5.0, 8.0)
        log.record_gantt_entry("Task3", 8.0, 12.0)
        
        assert len(log.gantt_data) == 3
        assert log.gantt_data[0] == ("Task1", 0.0, 5.0)
        assert log.gantt_data[1] == ("Task2", 5.0, 8.0)
        assert log.gantt_data[2] == ("Task3", 8.0, 12.0)
    
    def test_record_gantt_entry_same_task_multiple_times(self):
        """Test recording same task multiple times (e.g., preemption)"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("Task1", 0.0, 3.0)
        log.record_gantt_entry("Task2", 3.0, 6.0)
        log.record_gantt_entry("Task1", 6.0, 8.0)
        
        assert len(log.gantt_data) == 3
        task1_entries = [e for e in log.gantt_data if e[0] == "Task1"]
        assert len(task1_entries) == 2
    
    def test_record_gantt_entry_float_times(self):
        """Test recording gantt entries with floating point times"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("Task1", 0.5, 2.75)
        log.record_gantt_entry("Task2", 2.75, 5.125)
        
        assert log.gantt_data[0][1] == 0.5
        assert log.gantt_data[0][2] == 2.75
        assert log.gantt_data[1][1] == 2.75
    
    def test_record_gantt_entry_zero_duration(self):
        """Test recording gantt entry with zero duration"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("Task1", 5.0, 5.0)
        
        assert len(log.gantt_data) == 1
        assert log.gantt_data[0] == ("Task1", 5.0, 5.0)
    
    def test_record_gantt_entry_stores_tuple(self):
        """Test that gantt_data stores tuples in correct format"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("MyTask", 1.0, 4.0)
        
        entry = log.gantt_data[0]
        assert isinstance(entry, tuple)
        assert len(entry) == 3
        assert entry[0] == "MyTask"
        assert entry[1] == 1.0
        assert entry[2] == 4.0
    
    def test_record_gantt_entry_with_various_task_ids(self):
        """Test recording gantt entries with various task ID formats"""
        log = logger.CFSLogger()
        
        task_ids = ["Task1", "Task_2", "TASK3", "task4", "T5"]
        
        for i, tid in enumerate(task_ids):
            log.record_gantt_entry(tid, float(i*3), float((i+1)*3))
        
        assert len(log.gantt_data) == len(task_ids)
        for i, tid in enumerate(task_ids):
            assert log.gantt_data[i][0] == tid
    
    def test_gantt_data_is_list(self):
        """Test that gantt_data is initialized as a list"""
        log = logger.CFSLogger()
        assert isinstance(log.gantt_data, list)
    
    def test_record_gantt_entry_accumulates(self):
        """Test that gantt_data accumulates entries without reset"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("Task1", 0.0, 2.0)
        first_count = len(log.gantt_data)
        
        log.record_gantt_entry("Task2", 2.0, 4.0)
        second_count = len(log.gantt_data)
        
        assert second_count == first_count + 1


class TestCFSLoggerPrintGantt:
    """Tests for CFSLogger.print_gantt() method"""
    
    def test_print_gantt_with_no_data(self, capsys):
        """Test print_gantt() with no gantt data"""
        log = logger.CFSLogger()
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        assert "GANTT CHART" in captured.out
        assert "No data" in captured.out
    
    def test_print_gantt_with_single_task(self, capsys):
        """Test print_gantt() with single task and single burst"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 5.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        assert "GANTT CHART" in output
        assert "Task1" in output
    
    def test_print_gantt_with_multiple_tasks(self, capsys):
        """Test print_gantt() with multiple tasks"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 3.0)
        log.record_gantt_entry("Task2", 3.0, 6.0)
        log.record_gantt_entry("Task3", 6.0, 10.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        assert "GANTT CHART" in output
        assert "Task1" in output
        assert "Task2" in output
        assert "Task3" in output
    
    def test_print_gantt_with_preemption(self, capsys):
        """Test print_gantt() with task preemption (same task multiple times)"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 2.0)
        log.record_gantt_entry("Task2", 2.0, 5.0)
        log.record_gantt_entry("Task1", 5.0, 7.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        assert "GANTT CHART" in output
        assert "Task1" in output
        assert "Task2" in output
    
    def test_print_gantt_separator_lines(self, capsys):
        """Test that print_gantt() includes separator lines"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 5.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        # Should have = lines for header/footer
        assert "=" in output
    
    def test_print_gantt_includes_timeline(self, capsys):
        """Test that print_gantt() includes timeline/ruler"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 10.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        # Should have time scale
        assert "Time" in output or "ms" in output
    
    def test_print_gantt_visual_representation(self, capsys):
        """Test that print_gantt() includes visual blocks"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 5.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        # Should have visual blocks (█) or something similar
        assert "█" in output or "|" in output
    
    def test_print_gantt_to_file(self, tmp_path):
        """Test that print_gantt() writes to file when configured"""
        output_file = tmp_path / "gantt_log.txt"
        log = logger.CFSLogger(output_file=str(output_file))
        
        log.record_gantt_entry("Task1", 0.0, 5.0)
        log.print_gantt()
        
        with open(output_file, 'r') as f:
            content = f.read()
        
        assert "GANTT CHART" in content
        assert "Task" in content
    
    def test_print_gantt_multiple_calls(self, capsys):
        """Test multiple print_gantt() calls"""
        log = logger.CFSLogger()
        
        log.record_gantt_entry("Task1", 0.0, 5.0)
        log.print_gantt()
        
        log.record_gantt_entry("Task2", 5.0, 10.0)
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Both gantt charts should be printed
        assert output.count("GANTT CHART") == 2
    
    def test_print_gantt_task_ordering(self, capsys):
        """Test that tasks appear in sorted order"""
        log = logger.CFSLogger()
        
        # Add tasks out of order
        log.record_gantt_entry("Task3", 6.0, 9.0)
        log.record_gantt_entry("Task1", 0.0, 3.0)
        log.record_gantt_entry("Task2", 3.0, 6.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Find positions of task names
        pos1 = output.find("Task1")
        pos2 = output.find("Task2")
        pos3 = output.find("Task3")
        
        # Tasks should appear in numeric order (Task1 before Task2 before Task3)
        assert pos1 > -1 and pos2 > -1 and pos3 > -1
        assert pos1 < pos2 < pos3
    
    def test_print_gantt_with_zero_duration_task(self, capsys):
        """Test print_gantt() with zero-duration tasks"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 0.0)
        log.record_gantt_entry("Task2", 0.0, 5.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        assert "GANTT CHART" in output
    
    def test_print_gantt_with_large_time_values(self, capsys):
        """Test print_gantt() with large time values"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 1000.0)
        log.record_gantt_entry("Task2", 1000.0, 2000.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        assert "GANTT CHART" in output
        assert "Task" in output
    
    def test_print_gantt_formatting_consistency(self, capsys):
        """Test that print_gantt() formatting is consistent"""
        log = logger.CFSLogger()
        log.record_gantt_entry("Task1", 0.0, 5.0)
        log.record_gantt_entry("Task2", 5.0, 10.0)
        
        log.print_gantt()
        
        captured = capsys.readouterr()
        output = captured.out
        
        lines = output.strip().split('\n')
        # Should have header, data, and footer lines
        assert len(lines) >= 3

