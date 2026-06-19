package com.cmw.adaptiveBenchmark.workload;

public class BurstTask extends AdaptiveTask {

    private final long burstIterations;
    private final long pauseMs;
    private final int bursts;

    public BurstTask(long burstIterations, long pauseMs, int bursts) {
        this.burstIterations = burstIterations;
        this.pauseMs = pauseMs;
        this.bursts = bursts;
    }

    @Override
    protected void execute() {
        for (int b = 0; b < bursts; b++) {
            // CPU burst
            long x = 0;
            for (long i = 0; i < burstIterations; i++) {
                x += i;
            }
            // pausa entre bursts
            if (b < bursts - 1) {
                try {
                    Thread.sleep(pauseMs);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }

    @Override
    public TaskPriority priority() {
        return TaskPriority.HIGH;
    }

    @Override
    public String workloadName() {
        return "burst";
    }
}