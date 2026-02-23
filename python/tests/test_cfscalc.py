"""Unit testing for CFSCalculator class"""
import pytest

import src.cfscalc as cfscalc
import src.runqueue as runqueue
import src.task as task


class TestCFSCalculatorConstants:
    """Tests for CFSCalculator constants"""
    
    def test_constants_are_defined(self):
        """Test that all required constants are defined"""
        calc = cfscalc.CFSCalculator()
        assert hasattr(calc, 'L')
        assert hasattr(calc, 'MIN_GRANULARITY')
        assert hasattr(calc, 'NICE_0_WEIGTH')
    
    def test_scheduler_latency_value(self):
        """Test that scheduler latency (L) has correct value"""
        calc = cfscalc.CFSCalculator()
        assert calc.L == 6.0
    
    def test_min_granularity_value(self):
        """Test that minimum granularity has correct value"""
        calc = cfscalc.CFSCalculator()
        assert calc.MIN_GRANULARITY == 0.75
    
    def test_nice_0_weight_value(self):
        """Test that NICE_0_WEIGTH has correct value"""
        calc = cfscalc.CFSCalculator()
        assert calc.NICE_0_WEIGTH == 1024


class TestCalcCurTimeSlice:
    """Tests for CFSCalculator.calc_cur_time_slice() method"""
    
    def test_single_task_time_slice(self):
        """Test time slice calculation with a single task"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        rq.tasks.append(t1)
        
        time_slice = calc.calc_cur_time_slice(rq, t1)
        # Single task with no competition should get full latency
        assert time_slice == calc.L
    
    def test_multiple_tasks_equal_weight(self):
        """Test time slice calculation with multiple equal-weight tasks"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        rq.tasks = [t1, t2]
        
        time_slice_1 = calc.calc_cur_time_slice(rq, t1)
        time_slice_2 = calc.calc_cur_time_slice(rq, t2)
        # Equal weight tasks should have equal time slices
        expected_slice = calc.L / 2
        assert time_slice_1 == expected_slice
        assert time_slice_2 == expected_slice
    
    def test_multiple_tasks_different_nice_values(self):
        """Test time slice calculation with different nice values"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, -5, [("CPU", 5)])
        rq.tasks = [t1, t2]
        
        time_slice_1 = calc.calc_cur_time_slice(rq, t1)
        time_slice_2 = calc.calc_cur_time_slice(rq, t2)
        # Task with lower nice value (higher priority) should have larger time slice
        assert time_slice_2 > time_slice_1
    
    def test_time_slices_sum_to_latency(self):
        """Test that time slices sum to scheduler latency for equal-weight tasks"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        for i in range(4):
            t = task.Task(f"Task{i}", 0.0, 0, [("CPU", 5)])
            rq.tasks.append(t)
        
        total_slice = 0.0
        for t in rq.tasks:
            time_slice = calc.calc_cur_time_slice(rq, t)
            total_slice += time_slice
        
        assert total_slice == calc.L
    
    def test_time_slices_proportional_to_weight(self):
        """Test that time slices are proportional to task weights"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 5, [("CPU", 5)])
        rq.tasks = [t1, t2]
        
        time_slice_1 = calc.calc_cur_time_slice(rq, t1)
        time_slice_2 = calc.calc_cur_time_slice(rq, t2)
        
        # Ratio of time slices should match ratio of weights
        w1 = t1.get_task_weight()
        w2 = t2.get_task_weight()
        weight_ratio = w1 / w2
        slice_ratio = time_slice_1 / time_slice_2
        
        assert pytest.approx(slice_ratio) == pytest.approx(weight_ratio)
    
    def test_empty_queue(self):
        """Test time slice calculation with empty runqueue"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        # Empty queue - create a task not in queue to test
        t = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        
        # Should handle gracefully or raise appropriate error
        # Since task not in queue, total weight is 0
        try:
            time_slice = calc.calc_cur_time_slice(rq, t)
            # If no exception, verify it's a valid number (likely inf or 0)
            assert isinstance(time_slice, (int, float))
        except ZeroDivisionError:
            # It's acceptable to raise division by zero for empty queue
            pass


class TestUpdateVruntime:
    """Tests for CFSCalculator.update_vruntime() method"""
    
    def test_update_vruntime_single_task_zero_exec_time(self):
        """Test vruntime update with zero execution time"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t1.exec_time = 0.0
        rq.tasks.append(t1)
        
        calc.update_vruntime(rq)
        assert t1.vruntime == calc.MIN_GRANULARITY
    
    def test_update_vruntime_respects_min_granularity(self):
        """Test that vruntime respects minimum granularity constraint"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t1.exec_time = 0.1  # Very small execution time
        rq.tasks.append(t1)
        
        calc.update_vruntime(rq)
        assert t1.vruntime >= calc.MIN_GRANULARITY
    
    def test_update_vruntime_different_nice_values(self):
        """Test vruntime update with different nice values"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, -5, [("CPU", 5)])
        
        t1.exec_time = 10.0
        t2.exec_time = 10.0
        rq.tasks = [t1, t2]
        
        calc.update_vruntime(rq)
        
        # Task with higher nice value (lower priority) should have higher vruntime
        assert t1.vruntime > t2.vruntime
    
    def test_update_vruntime_multiple_tasks(self):
        """Test vruntime update with multiple tasks"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        t3 = task.Task("Task3", 0.0, 0, [("CPU", 5)])
        
        t1.exec_time = 10.0
        t2.exec_time = 10.0
        t3.exec_time = 10.0
        rq.tasks = [t1, t2, t3]
        
        calc.update_vruntime(rq)
        
        # All tasks should have the same vruntime (equal nice values)
        assert t1.vruntime == t2.vruntime == t3.vruntime
    
    def test_update_vruntime_proportional_to_exec_time(self):
        """Test that vruntime is proportional to execution time"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        
        t1.exec_time = 5.0
        t2.exec_time = 10.0
        rq.tasks = [t1, t2]
        
        calc.update_vruntime(rq)
        
        # Task with double execution time should have roughly double vruntime
        assert t2.vruntime > t1.vruntime
        # The ratio should be approximately 2 (unless MIN_GRANULARITY constraint applies)
        if t1.vruntime >= calc.MIN_GRANULARITY and t2.vruntime >= calc.MIN_GRANULARITY:
            ratio = t2.vruntime / t1.vruntime
            assert pytest.approx(ratio, rel=0.1) == 2.0
    
    def test_update_vruntime_empty_queue(self):
        """Test vruntime update with empty runqueue"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        # Should not raise any exception
        calc.update_vruntime(rq)
    
    def test_update_vruntime_nice_to_weight_formula(self):
        """Test vruntime calculation matches expected formula"""
        calc = cfscalc.CFSCalculator()
        rq = runqueue.Runqueue()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t1.exec_time = 100.0
        rq.tasks.append(t1)
        
        calc.update_vruntime(rq)
        
        # Expected vruntime: max(MIN_GRANULARITY, exec_time * NICE_0_WEIGHT / weight)
        expected = max(
            calc.MIN_GRANULARITY,
            t1.exec_time * calc.NICE_0_WEIGTH / t1.get_task_weight()
        )
        assert t1.vruntime == expected
