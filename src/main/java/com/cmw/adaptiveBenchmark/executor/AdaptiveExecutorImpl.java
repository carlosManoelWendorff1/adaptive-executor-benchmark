package com.cmw.adaptiveBenchmark.executor;

import java.util.List;

import com.cmw.adaptive.AdaptiveExecutor;
import com.cmw.adaptive.scaling.PidScalingStrategy;
import com.cmw.adaptive.task.TaskContext;
import com.cmw.adaptive.task.TrackedTask;
import com.cmw.adaptive.task.enums.TaskPriority;
import com.cmw.adaptiveBenchmark.workload.AdaptiveTask;

public class AdaptiveExecutorImpl {

    private final AdaptiveExecutor executor;

    public AdaptiveExecutorImpl() {
        this.executor = new AdaptiveExecutor(
                1,
                16,
                new PidScalingStrategy(0.5, 0.01, 0.3));
    }

    public void execute(List<AdaptiveTask> tasks)
            throws InterruptedException {

        long baseline = executor.metrics().completedTasks();

        for (AdaptiveTask task : tasks) {
            executor.submit(toTrackedTask(task));
        }

        while ((executor.metrics().completedTasks() - baseline) < tasks.size()) {
            Thread.sleep(5);
        }
    }

    public void shutdown() throws InterruptedException {
        executor.shutdown();
    }

    private TrackedTask toTrackedTask(AdaptiveTask benchmarkTask) {

        com.cmw.adaptive.task.AdaptiveTask libTask = new com.cmw.adaptive.task.AdaptiveTask() {

            @Override
            public TaskPriority priority() {
                return switch (benchmarkTask.priority()) {
                    case HIGH -> TaskPriority.HIGH;
                    case LOW -> TaskPriority.LOW;
                };
            }

            @Override
            public void run() {
                try {
                    benchmarkTask.call();
                } catch (Exception e) {
                    Thread.currentThread().interrupt();
                }
            }
        };

        return new TrackedTask(libTask, new TaskContext());
    }
}