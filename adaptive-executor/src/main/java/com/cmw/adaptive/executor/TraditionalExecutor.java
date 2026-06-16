package com.cmw.adaptive.executor;

import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import com.cmw.adaptive.workload.AdaptiveTask;

public class TraditionalExecutor {

    private final ExecutorService executor;

    public TraditionalExecutor(int workers) {
        this.executor = Executors.newFixedThreadPool(workers);
    }

    public void execute(List<AdaptiveTask> tasks)
            throws InterruptedException {

        executor.invokeAll(tasks);
    }

    public void shutdown()
            throws InterruptedException {

        executor.shutdown();

        executor.awaitTermination(
                1,
                TimeUnit.HOURS);
    }
}