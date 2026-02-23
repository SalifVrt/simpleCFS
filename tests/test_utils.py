"""Unit testing for Formatting utils"""
import pytest

import src.utils as utils

class TestFormatTask:
    """Tests for utils.format_task() function"""
    
    def test_format_task_single_cpu_burst(self):
        """Test formatting a task with a single CPU burst"""
        line = ["A", 0, 0, 10]
        result = utils.format_task(line)
        assert result[0] == "A"
        assert result[1] == 0
        assert result[2] == 0
        assert result[3] == [("CPU", 10)]
    
    def test_format_task_cpu_and_io_bursts(self):
        """Test formatting a task with alternating CPU and IO bursts"""
        line = ["B", 0, -4, 2, 5, 2, 5]
        result = utils.format_task(line)
        assert result[0] == "B"
        assert result[1] == 0
        assert result[2] == -4
        assert result[3] == [("CPU", 2), ("IO", 5), ("CPU", 2), ("IO", 5)]
    
    def test_format_task_multiple_bursts(self):
        """Test formatting a task with multiple alternating bursts"""
        line = ["C", 5, 2, 1, 8, 1, 8, 3, 4]
        result = utils.format_task(line)
        assert result[0] == "C"
        assert result[1] == 5
        assert result[2] == 2
        assert result[3] == [("CPU", 1), ("IO", 8), ("CPU", 1), ("IO", 8), ("CPU", 3), ("IO", 4)]
    
    def test_format_task_preserves_original_fields(self):
        """Test that pid, arrival_time, and nice are preserved"""
        line = ["Task_X", 42, -10, 100, 200]
        result = utils.format_task(line)
        assert result[0] == "Task_X"
        assert result[1] == 42
        assert result[2] == -10


class TestFileToTasks:
    """Tests for utils.file_to_tasks() function"""
    
    def test_file_to_tasks_reads_correct_number_of_tasks(self, fpath):
        """Test that correct number of tasks are read from file"""
        tasks = utils.file_to_tasks(fpath)
        assert len(tasks) == 4  # td1.txt has 4 tasks
    
    def test_file_to_tasks_formats_correctly(self, fpath):
        """Test that tasks are formatted correctly from file"""
        tasks = utils.file_to_tasks(fpath)
        
        # Check first task (A)
        assert tasks[0][0] == "A"
        assert tasks[0][1] == 0
        assert tasks[0][2] == 0
        assert len(tasks[0][3]) == 4
        assert tasks[0][3][0] == ("CPU", 1)
        assert tasks[0][3][1] == ("IO", 8)
    
    def test_file_to_tasks_parses_bursts_as_tuples(self, fpath):
        """Test that all bursts are tuples with proper labels"""
        tasks = utils.file_to_tasks(fpath)
        
        for task in tasks:
            bursts = task[3]
            for i, burst in enumerate(bursts):
                assert isinstance(burst, tuple)
                assert len(burst) == 2
                if i % 2 == 0:
                    assert burst[0] == "CPU"
                else:
                    assert burst[0] == "IO"
