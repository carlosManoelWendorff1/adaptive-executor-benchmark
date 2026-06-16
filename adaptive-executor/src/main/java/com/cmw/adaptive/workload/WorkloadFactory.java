package com.cmw.adaptive.workload;

import java.util.ArrayList;
import java.util.List;

public class WorkloadFactory {

    public static List<AdaptiveTask> createTasks(
            int payments,
            int analytics,
            long paymentSleepMs,
            long analyticsIterations) {

        List<AdaptiveTask> tasks = new ArrayList<>();

        for (int i = 0; i < payments; i++) {
            tasks.add(
                    new PaymentTask(paymentSleepMs));
        }

        for (int i = 0; i < analytics; i++) {
            tasks.add(
                    new AnalyticsTask(analyticsIterations));
        }

        return tasks;
    }
}