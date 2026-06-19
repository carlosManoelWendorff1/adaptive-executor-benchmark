package com.cmw.adaptiveBenchmark.workload;

import java.util.ArrayList;
import java.util.List;

public class WorkloadFactory {

    public static List<AdaptiveTask> createTasks(
            int payments,
            int analytics,
            int bursts,
            long paymentSleepMs,
            long analyticsIterations,
            long burstIterations,
            long burstPauseMs,
            int burstCount) {

        List<AdaptiveTask> tasks = new ArrayList<>();

        for (int i = 0; i < payments; i++) {
            tasks.add(new PaymentTask(paymentSleepMs));
        }

        for (int i = 0; i < analytics; i++) {
            tasks.add(new AnalyticsTask(analyticsIterations));
        }

        for (int i = 0; i < bursts; i++) {
            tasks.add(new BurstTask(burstIterations, burstPauseMs, burstCount));
        }

        return tasks;
    }
}