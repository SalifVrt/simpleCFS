"""Unit testing for Runqueue class"""
import pytest

import src.runqueue as runqueue
import src.task as task


class TestGetMinVruntime:
    """Tests for runqueue.Runqueue.get_min_vruntime() method"""
    
    def test_get_min_vruntime_empty_queue(self):
        """Test get_min_vruntime returns None for empty queue"""
        rq = runqueue.Runqueue()
        result = rq.get_min_vruntime()
        assert result is None
    
    def test_get_min_vruntime_single_task(self):
        """Test get_min_vruntime with a single task"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        rq.tasks.append(t1)
        
        result = rq.get_min_vruntime()
        assert result is not None
        index, min_task = result
        assert index == 0
        assert min_task == t1
        assert min_task.vruntime == 0.0
    
    def test_get_min_vruntime_multiple_tasks(self):
        """Test get_min_vruntime returns task with minimum vruntime"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        t3 = task.Task("Task3", 0.0, 0, [("CPU", 5)])
        
        t1.vruntime = 10.0
        t2.vruntime = 5.0
        t3.vruntime = 15.0
        
        rq.tasks = [t1, t2, t3]
        
        result = rq.get_min_vruntime()
        assert result is not None
        index, min_task = result
        assert index == 1
        assert min_task == t2
        assert min_task.vruntime == 5.0
    
    def test_get_min_vruntime_equal_vruntime(self):
        """Test get_min_vruntime with equal vruntime values returns first"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        
        t1.vruntime = 10.0
        t2.vruntime = 10.0
        
        rq.tasks = [t1, t2]
        
        result = rq.get_min_vruntime()
        if result:
            index, min_task = result
            assert index == 0  # Should return the first one
            assert min_task == t1
    
    def test_get_min_vruntime_after_vruntime_update(self):
        """Test get_min_vruntime correctly identifies task after vruntime changes"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        
        t1.vruntime = 5.0
        t2.vruntime = 10.0
        rq.tasks = [t1, t2]
        
        result = rq.get_min_vruntime()
        if result:
            assert result[0] == 0
        
        # Update t1's vruntime
        t1.vruntime = 20.0
        result = rq.get_min_vruntime()
        if result:
            assert result[0] == 1
            assert result[1] == t2


class TestPickNextTask:
    """Tests for runqueue.Runqueue.pick_next_task() method"""
    
    def test_pick_next_task_empty_queue(self):
        """Test pick_next_task returns None for empty queue"""
        rq = runqueue.Runqueue()
        result = rq.pick_next_task()
        assert result is None
    
    def test_pick_next_task_single_task(self):
        """Test pick_next_task returns single task"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        rq.tasks.append(t1)
        
        result = rq.pick_next_task()
        assert result == t1
    
    def test_pick_next_task_multiple_tasks(self):
        """Test pick_next_task returns task with minimum vruntime"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        t3 = task.Task("Task3", 0.0, 0, [("CPU", 5)])
        
        t1.vruntime = 15.0
        t2.vruntime = 3.0
        t3.vruntime = 20.0
        
        rq.tasks = [t1, t2, t3]
        
        result = rq.pick_next_task()
        assert result == t2  # t2 has minimum vruntime
    
    def test_pick_next_task_returns_correct_type(self):
        """Test pick_next_task returns a Task object"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        rq.tasks.append(t1)
        
        result = rq.pick_next_task()
        assert isinstance(result, task.Task)
    
    def test_pick_next_task_zero_vruntime(self):
        """Test pick_next_task with all tasks having zero vruntime"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        
        rq.tasks = [t1, t2]
        
        result = rq.pick_next_task()
        assert result == t1  # Should return first one


class TestRunqueueIntegration:
    """Integration tests for Runqueue methods"""
    
    def test_get_min_and_pick_next_task_consistency(self):
        """Test that pick_next_task matches get_min_vruntime task"""
        rq = runqueue.Runqueue()
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        t3 = task.Task("Task3", 0.0, 0, [("CPU", 5)])
        
        t1.vruntime = 10.0
        t2.vruntime = 2.0
        t3.vruntime = 8.0
        
        rq.tasks = [t1, t2, t3]
        
        min_result = rq.get_min_vruntime()
        pick_result = rq.pick_next_task()
        
        if min_result:
            assert min_result[1] == pick_result
