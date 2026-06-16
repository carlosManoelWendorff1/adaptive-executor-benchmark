package com.cmw.adaptive.benchmark;

import java.util.List;
import java.util.concurrent.TimeUnit;

import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Level;
import org.openjdk.jmh.annotations.Mode;
import org.openjdk.jmh.annotations.OutputTimeUnit;
import org.openjdk.jmh.annotations.Param;
import org.openjdk.jmh.annotations.Scope;
import org.openjdk.jmh.annotations.Setup;
import org.openjdk.jmh.annotations.State;
import org.openjdk.jmh.annotations.TearDown;

import com.cmw.adaptive.executor.TraditionalExecutor;
import com.cmw.adaptive.helpers.ApplicationProperties;
import com.cmw.adaptive.helpers.noise.CpuNoiseGenerator;
import com.cmw.adaptive.workload.AdaptiveTask;
import com.cmw.adaptive.workload.WorkloadFactory;

@BenchmarkMode(Mode.Throughput)
@OutputTimeUnit(TimeUnit.SECONDS)
@State(Scope.Benchmark)
public class TraditionalBenchmark {

    @Param({ "2", "4", "8", "16" })
    private int workers;

    private TraditionalExecutor executor;
    private List<AdaptiveTask> tasks;
    private CpuNoiseGenerator noise;

    @Setup(Level.Trial)
    public void setup() {

        ApplicationProperties config = new ApplicationProperties();

        if (config.noiseEnabled()) {

            noise = new CpuNoiseGenerator(
                    config.noiseThreads());

            noise.start();
        }

        executor = new TraditionalExecutor(workers);

        tasks = WorkloadFactory.createTasks(
                config.payments(),
                config.analytics(),
                config.paymentSleepMs(),
                config.analyticsIterations());
    }

    @TearDown(Level.Trial)
    public void cleanup()
            throws InterruptedException {

        if (noise != null) {
            noise.stop();
        }

        executor.shutdown();
    }

    @Benchmark
    public void execute()
            throws InterruptedException {

        executor.execute(tasks);
    }
}