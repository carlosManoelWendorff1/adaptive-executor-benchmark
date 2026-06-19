package com.cmw.adaptiveBenchmark.helpers;

import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.List;
import java.util.Properties;
import java.util.stream.Collectors;

public class ApplicationProperties {

    private final Properties properties = new Properties();

    public ApplicationProperties() {

        try (InputStream input = getClass()
                .getClassLoader()
                .getResourceAsStream("application.properties")) {

            if (input == null) {
                throw new RuntimeException(
                        "application.properties not found");
            }

            properties.load(input);

        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public List<Integer> workerConfigurations() {
        String workers = properties.getProperty("executor.workers");
        return Arrays.stream(workers.split(","))
                .map(String::trim)
                .map(Integer::parseInt)
                .collect(Collectors.toList());
    }

    public int payments() {
        return Integer.parseInt(
                properties.getProperty("workload.payments"));
    }

    public int analytics() {
        return Integer.parseInt(
                properties.getProperty("workload.analytics"));
    }

    public long analyticsIterations() {
        return Long.parseLong(
                properties.getProperty("analytics.iterations"));
    }

    public long paymentSleepMs() {
        return Long.parseLong(
                properties.getProperty("payment.sleep.ms"));
    }

    public boolean noiseEnabled() {
        return Boolean.parseBoolean(
                properties.getProperty("noise.enabled", "false"));
    }

    public int noiseThreads() {
        return Integer.parseInt(
                properties.getProperty("noise.threads", "0"));
    }

    public int bursts() {
        return Integer.parseInt(
                properties.getProperty("workload.bursts", "0"));
    }

    public long burstIterations() {
        return Long.parseLong(
                properties.getProperty("burst.iterations", "5000000"));
    }

    public long burstPauseMs() {
        return Long.parseLong(
                properties.getProperty("burst.pause.ms", "5"));
    }

    public int burstCount() {
        return Integer.parseInt(
                properties.getProperty("burst.count", "3"));
    }
}