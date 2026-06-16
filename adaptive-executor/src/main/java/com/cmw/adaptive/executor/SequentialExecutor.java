package com.cmw.adaptive.executor;

import java.util.List;

import com.cmw.adaptive.workload.AdaptiveTask;

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