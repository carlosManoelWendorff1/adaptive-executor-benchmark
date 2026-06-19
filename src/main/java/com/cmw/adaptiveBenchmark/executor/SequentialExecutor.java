package com.cmw.adaptiveBenchmark.executor;

import java.util.List;

import com.cmw.adaptiveBenchmark.workload.AdaptiveTask;

public class SequentialExecutor {

    public void execute(List<AdaptiveTask> tasks) {

        for (AdaptiveTask task : tasks) {

            try {
                task.call();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }
}