package com.cmw.adaptiveBenchmark.benchmark;

import java.util.List;
import java.util.concurrent.TimeUnit;

import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Level;
import org.openjdk.jmh.annotations.Mode;
import org.openjdk.jmh.annotations.OutputTimeUnit;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.Setup;
import org.openjdk.jmh.annotations.State;
import org.openjdk.jmh.annotations.TearDown;

import com.cmw.adaptiveBenchmark.executor.SequentialExecutor;
import com.cmw.adaptiveBenchmark.helpers.ApplicationProperties;
import com.cmw.adaptiveBenchmark.helpers.noise.CpuNoiseGenerator;
import com.cmw.adaptiveBenchmark.workload.AdaptiveTask;
import com.cmw.adaptiveBenchmark.workload.WorkloadFactory;

@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
@State(Scope.Benchmark)
public class SequentialBenchmark {

    private List<AdaptiveTask> tasks;
    private SequentialExecutor executor;
    private CpuNoiseGenerator noise;

    @Setup(Level.Trial)
    public void setup() {

        ApplicationProperties config = new ApplicationProperties();

        if (config.noiseEnabled()) {

            noise = new CpuNoiseGenerator(
                    config.noiseThreads());

            noise.start();
        }

        tasks = WorkloadFactory.createTasks(
                config.payments(),
                config.analytics(),
                config.bursts(),
                config.paymentSleepMs(),
                config.analyticsIterations(),
                config.burstIterations(),
                config.burstPauseMs(),
                config.burstCount());

        executor = new SequentialExecutor();
    }

    @Benchmark
    public void execute() {

        executor.execute(tasks);
    }

    @TearDown(Level.Trial)
    public void cleanup() {

        if (noise != null) {
            noise.stop();
        }
    }
}