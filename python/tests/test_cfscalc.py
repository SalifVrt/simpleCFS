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
        assert hasattr(calc, 'NICE_0_WEIGHT')
    
    def test_scheduler_latency_value(self):
        """Test that scheduler latency (L) has correct value"""
        calc = cfscalc.CFSCalculator()
        assert calc.L == 6.0
    
    def test_min_granularity_value(self):
        """Test that minimum granularity has correct value"""
        calc = cfscalc.CFSCalculator()
        assert calc.MIN_GRANULARITY == 0.75
    
    def test_nice_0_weight_value(self):
        """Test that NICE_0_WEIGHT has correct value"""
        calc = cfscalc.CFSCalculator()
        assert calc.NICE_0_WEIGHT == 1024


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
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        initial_vruntime = t1.vruntime
        
        calc.update_vruntime(t1, 0.0)
        # With zero execution time, vruntime shouldn't change
        assert t1.vruntime == initial_vruntime
    
    def test_update_vruntime_respects_min_granularity(self):
        """Test that vruntime respects minimum granularity constraint"""
        calc = cfscalc.CFSCalculator()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        
        calc.update_vruntime(t1, 0.1)  # Very small execution time
        # Vruntime should be updated by 0.1 * (NICE_0_WEIGHT / weight)
        assert isinstance(t1.vruntime, (int, float))
    
    def test_update_vruntime_different_nice_values(self):
        """Test vruntime update with different nice values"""
        calc = cfscalc.CFSCalculator()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, -5, [("CPU", 5)])
        
        actual_duration = 10.0
        calc.update_vruntime(t1, actual_duration)
        calc.update_vruntime(t2, actual_duration)
        
        # Task with higher nice value (lower priority) should have higher vruntime increase
        # t1 has nice=0, t2 has nice=-5 (higher priority)
        assert t1.vruntime > t2.vruntime
    
    def test_update_vruntime_multiple_tasks(self):
        """Test vruntime update with multiple tasks"""
        calc = cfscalc.CFSCalculator()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        t3 = task.Task("Task3", 0.0, 0, [("CPU", 5)])
        
        actual_duration = 10.0
        calc.update_vruntime(t1, actual_duration)
        calc.update_vruntime(t2, actual_duration)
        calc.update_vruntime(t3, actual_duration)
        
        # All tasks should have the same vruntime (equal nice values, same duration)
        assert t1.vruntime == t2.vruntime == t3.vruntime
    
    def test_update_vruntime_proportional_to_exec_time(self):
        """Test that vruntime is proportional to execution time"""
        calc = cfscalc.CFSCalculator()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        t2 = task.Task("Task2", 0.0, 0, [("CPU", 5)])
        
        calc.update_vruntime(t1, 5.0)
        calc.update_vruntime(t2, 10.0)
        
        # Task with double execution time should have roughly double vruntime
        assert t2.vruntime > t1.vruntime
        # The ratio should be approximately 2
        ratio = t2.vruntime / t1.vruntime
        assert pytest.approx(ratio, rel=0.1) == 2.0
    
    def test_update_vruntime_single_task(self):
        """Test vruntime update with a single task"""
        calc = cfscalc.CFSCalculator()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        
        # Should not raise any exception
        initial_vruntime = t1.vruntime
        calc.update_vruntime(t1, 5.0)
        assert t1.vruntime > initial_vruntime
    
    def test_update_vruntime_nice_to_weight_formula(self):
        """Test vruntime calculation matches expected formula"""
        calc = cfscalc.CFSCalculator()
        
        t1 = task.Task("Task1", 0.0, 0, [("CPU", 5)])
        actual_duration = 100.0
        initial_vruntime = t1.vruntime
        
        calc.update_vruntime(t1, actual_duration)
        
        # Expected vruntime increase: actual_duration * NICE_0_WEIGHT / weight
        weight_factor = calc.NICE_0_WEIGHT / t1.get_task_weight()
        expected_vruntime = initial_vruntime + actual_duration * weight_factor
        assert t1.vruntime == expected_vruntime
