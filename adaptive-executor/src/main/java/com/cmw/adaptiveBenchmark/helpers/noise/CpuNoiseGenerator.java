package com.cmw.adaptiveBenchmark.helpers.noise;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public class CpuNoiseGenerator implements NoiseGenerator {

    private final int threads;
    private final AtomicBoolean running = new AtomicBoolean(false);
    private final List<Thread> workers = new ArrayList<>();

    public CpuNoiseGenerator(int threads) {
        this.threads = threads;
    }

    @Override
    public void start() {

        if (running.get()) {
            return;
        }

        running.set(true);

        for (int i = 0; i < threads; i++) {

            Thread worker = Thread.ofPlatform()
                    .name("noise-" + i)
                    .start(() -> {

                        while (running.get()) {

                            double result = 0;

                            for (int j = 0; j < 1_000_000; j++) {
                                result += Math.sqrt(j);
                            }

                            if (result == -1) {
                                System.out.println(result);
                            }
                        }
                    });

            workers.add(worker);
        }
    }

    @Override
    public void stop() {

        running.set(false);

        for (Thread worker : workers) {

            try {
                worker.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        workers.clear();
    }
}