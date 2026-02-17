"""Unit testing for Task class"""
import pytest

import src.task as task
import src.utils as utils

class TestTaskInitialization:
    """Tests for task.Task class initialization"""
    
    def test_task_init_sets_attributes(self):
        """Test that Task initialization sets all attributes correctly"""
        bursts = [("CPU", 5), ("IO", 10), ("CPU", 3)]
        t = task.Task("Task1", 0.0, -2, bursts)
        
        assert t.id == "Task1"
        assert t.arrival_time == 0.0
        assert t.nice == -2
        assert t.bursts == bursts
    
    def test_task_init_sets_default_state(self):
        """Test that new task has None state and 0 vruntime"""
        bursts = [("CPU", 5)]
        t = task.Task("Task2", 1.0, 0, bursts)
        
        assert t.vruntime == 0.0
        assert t.state is None
        assert t.current_burst == 0
    
    def test_task_init_with_different_nice_values(self):
        """Test Task initialization with various nice values"""
        bursts = [("CPU", 1)]
        
        t1 = task.Task("T1", 0.0, -20, bursts)
        assert t1.nice == -20
        
        t2 = task.Task("T2", 0.0, 0, bursts)
        assert t2.nice == 0
        
        t3 = task.Task("T3", 0.0, 19, bursts)
        assert t3.nice == 19


class TestTaskIsFinished:
    """Tests for task.Task.is_finished() method"""
    
    def test_is_finished_false_initially(self):
        """Test that task is not finished when created"""
        bursts = [("CPU", 5), ("IO", 10)]
        t = task.Task("Task1", 0.0, 0, bursts)
        assert t.is_finished() is False
    
    def test_is_finished_false_during_execution(self):
        """Test that task is not finished mid-execution"""
        bursts = [("CPU", 5), ("IO", 10), ("CPU", 3)]
        t = task.Task("Task1", 0.0, 0, bursts)
        t.current_burst = 1
        assert t.is_finished() is False
    
    def test_is_finished_true_after_completion(self):
        """Test that task is finished when current_burst equals burst count"""
        bursts = [("CPU", 5), ("IO", 10), ("CPU", 3)]
        t = task.Task("Task1", 0.0, 0, bursts)
        t.current_burst = len(bursts)
        assert t.is_finished() is True
    
    def test_is_finished_single_burst(self):
        """Test is_finished with single burst task"""
        bursts = [("CPU", 20)]
        t = task.Task("Task1", 0.0, 0, bursts)
        assert t.is_finished() is False
        t.current_burst = 1
        assert t.is_finished() is True
    
    def test_is_finished_empty_bursts(self):
        """Test is_finished with empty bursts list"""
        bursts = []
        t = task.Task("Task1", 0.0, 0, bursts)
        assert t.is_finished() is True


class TestTaskIntegration:
    """Integration tests with formatted tasks from file"""
    
    def test_task_from_formatted_data(self, td1_path):
        """Test creating Task objects from formatted task data"""
        tasks_data = utils.file_to_tasks(td1_path)
        
        # Create task from first formatted task
        task_data = tasks_data[0]
        t = task.Task(task_data[0], int(task_data[1]), int(task_data[2]), task_data[3])
        
        assert t.id == "A"
        assert t.arrival_time == 0
        assert t.nice == 0
        assert len(t.bursts) == 4
        assert t.is_finished() is False
    
    def test_task_burst_execution_simulation(self, td1_path):
        """Test simulating task burst execution"""
        tasks_data = utils.file_to_tasks(td1_path)
        task_data = tasks_data[1]  # Task B
        t = task.Task(task_data[0], int(task_data[1]), int(task_data[2]), task_data[3])
        
        # Simulate execution of bursts
        for i in range(len(t.bursts)):
            assert t.is_finished() is False
            burst_type, burst_time = t.bursts[i]
            assert burst_type in ["CPU", "IO"]
            t.current_burst += 1
        
        assert t.is_finished() is True