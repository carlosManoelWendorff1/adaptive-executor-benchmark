package com.cmw.adaptive.workload;

public class PaymentTask extends AdaptiveTask {

    private final long sleepMs;

    public PaymentTask(long sleepMs) {
        this.sleepMs = sleepMs;
    }

    @Override
    public TaskPriority priority() {
        return TaskPriority.HIGH;
    }

    @Override
    public String workloadName() {
        return "payment";
    }

    @Override
    protected void execute() {

        try {
            Thread.sleep(sleepMs);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}