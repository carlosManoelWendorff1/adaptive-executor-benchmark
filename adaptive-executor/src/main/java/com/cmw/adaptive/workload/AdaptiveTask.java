package com.cmw.adaptive.workload;

import java.util.concurrent.Callable;

public abstract class AdaptiveTask implements Callable<Void> {

    @Override
    public final Void call() {

        execute();

        return null;
    }

    protected abstract void execute();

    public abstract TaskPriority priority();

    public abstract String workloadName();
}