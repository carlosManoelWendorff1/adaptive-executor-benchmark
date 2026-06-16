package com.cmw.adaptive.workload;

public class AnalyticsTask extends AdaptiveTask {

    private final long iterations;

    public AnalyticsTask(long iterations) {
        this.iterations = iterations;
    }

    @Override
    public TaskPriority priority() {
        return TaskPriority.LOW;
    }

    @Override
    public String workloadName() {
        return "analytics";
    }

    @Override
    protected void execute() {

        long result = 0;

        for (long i = 0; i < iterations; i++) {
            result += Math.sqrt(i);
        }

        // impede otimização agressiva do JIT
        if (result == Long.MIN_VALUE) {
            System.out.println(result);
        }
    }
}