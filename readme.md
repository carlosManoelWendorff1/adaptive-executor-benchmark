# Adaptive Executor Benchmark

Benchmark project for evaluating adaptive thread pool execution strategies using [JMH (Java Microbenchmark Harness)](https://github.com/openjdk/jmh).

The goal is to compare throughput and scalability of multiple executor implementations under different workloads and CPU contention conditions, simulating real-world noisy neighbour scenarios common in shared infrastructure environments.

---

## Executors

### Sequential Executor

Executes all tasks sequentially in a single thread. Used as the baseline for speedup calculations.

### Traditional Executor

Fixed-size thread pool using `Executors.newFixedThreadPool(n)`. Benchmarked with `workers = {2, 4, 8, 16}` to evaluate how throughput scales with thread count.

### Adaptive Executor

Dynamic thread pool backed by a priority queue and a PID-based scaling strategy. Workers are created and destroyed at runtime based on queue size, CPU load, and throughput feedback. Tasks are scheduled by priority — `HIGH` tasks are always processed before `LOW` tasks.

Key components:

| Component            | Description                                                       |
| -------------------- | ----------------------------------------------------------------- |
| `PriorityTaskQueue`  | `PriorityBlockingQueue`-backed queue ordered by task priority     |
| `ScalingManager`     | Background thread that evaluates scaling decisions every 200ms    |
| `PidScalingStrategy` | PID controller that computes desired worker count from queue size |
| `ExecutorMetrics`    | Lock-free metrics via `AtomicLong`/`AtomicInteger`                |

---

## Workloads

### Payment Task (`HIGH` priority)

Simulates I/O-bound work such as payment processing with network latency.

```properties
payment.sleep.ms=10
workload.payments=100
```

### Analytics Task (`LOW` priority)

Simulates CPU-bound work such as data aggregation with heavy computation.

```properties
analytics.iterations=100000000
workload.analytics=100
```

### Burst Task (`HIGH` priority)

Simulates irregular CPU spikes — alternates between compute bursts and short pauses. Designed to stress the adaptive scaler's reaction time.

```properties
workload.bursts=50
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
```

---

## Noise Generator

Simulates CPU contention from co-located workloads (noisy neighbour effect). Background threads spin continuously during benchmark execution.

```properties
noise.enabled=true
noise.threads=4
```

---

## Configuration

All benchmark parameters are defined in:

```
src/main/resources/application.properties
```

Full example:

```properties
# Workloads
workload.payments=50
workload.analytics=50
workload.bursts=50

# Payment simulation (I/O-bound)
payment.sleep.ms=10

# Analytics simulation (CPU-bound)
analytics.iterations=100000000

# Burst simulation (irregular CPU spikes)
burst.iterations=5000000
burst.pause.ms=5
burst.count=3

# Traditional executor worker configurations
executor.workers=2,4,8,16

# Noise (noisy neighbour simulation)
noise.enabled=false
noise.threads=4
```

---

## Building

```bash
mvn clean package
```

Output: `target/benchmarks.jar`

> **Note:** The `application.properties` file is packaged inside the JAR. Any configuration change requires rebuilding.

---

## Running

### Single run

```bash
java -jar target/benchmarks.jar ".*Benchmark.*" -rf csv -rff results.csv -wi 3 -i 5 -f 2
```

### JMH parameters

| Parameter | Description            | Recommended       |
| --------- | ---------------------- | ----------------- |
| `-wi`     | Warmup iterations      | `3`               |
| `-i`      | Measurement iterations | `5`               |
| `-f`      | Fork count             | `2`               |
| `-rf`     | Result format          | `csv`             |
| `-rff`    | Output file            | `results/exp.csv` |

### Single benchmark

```bash
java -jar target/benchmarks.jar AdaptiveBenchmark
java -jar target/benchmarks.jar TraditionalBenchmark
java -jar target/benchmarks.jar SequentialBenchmark
```

---

## Automated Experiment Suite

The project includes a PowerShell script that runs all 10 planned experiments automatically, updating `application.properties` and recompiling before each run.

```powershell
.\run_experiments.ps1
```

Results are saved to `results/` with one CSV per experiment:

| File                   | Scenario                          |
| ---------------------- | --------------------------------- |
| `01_baseline_low.csv`  | Low load, no noise                |
| `02_baseline_med.csv`  | Medium load, no noise             |
| `03_baseline_high.csv` | High load, no noise               |
| `04_burst_low.csv`     | Light burst mix, no noise         |
| `05_burst_high.csv`    | Heavy burst, no noise             |
| `06_noise2_low.csv`    | Light noise (2 threads)           |
| `07_noise2_burst.csv`  | Light noise + burst               |
| `08_noise4_low.csv`    | Heavy noise (4 threads)           |
| `09_noise4_burst.csv`  | Heavy noise + burst               |
| `10_noise8_burst.csv`  | Extreme noise (8 threads) + burst |

---

## Result Visualization

Requires Python 3.12+ with `pandas`, `matplotlib`, and `numpy`.

```bash
pip install pandas matplotlib numpy
python generate_charts.py
```

Charts are saved to `charts/`:

| File                               | Description                                                |
| ---------------------------------- | ---------------------------------------------------------- |
| `01_throughput_per_experiment.png` | Grouped bar chart — throughput per executor per experiment |
| `02_adaptive_vs_traditional16.png` | Adaptive vs Traditional w=16 across all scenarios          |
| `03_noise_degradation.png`         | Throughput degradation curve under increasing noise        |
| `04_speedup_over_sequential.png`   | Speedup of each executor relative to sequential baseline   |
| `05_speedup_linear.png`            | Speedup vs linear ideal — one subplot per experiment       |
| `summary.csv`                      | Consolidated results with adaptive vs best traditional (%) |

---

## Interpreting Results

- **Speedup** is computed relative to the `SequentialBenchmark` baseline.
- **Linear ideal** represents perfect parallelism — speedup equal to worker count.
- The adaptive executor's speedup appears as a horizontal line in chart 05, showing the equivalent number of fixed workers it autonomously matched.
- `adaptive_vs_best_%` in `summary.csv` shows how the adaptive executor compares to `Traditional w=16`: negative means it underperformed, positive means it outperformed.

---

## Notes

- Results vary with hardware, JVM version, OS scheduler, and background activity.
- Always use the same `application.properties` when comparing executors.
- The adaptive executor includes a ~200ms scaling reaction delay — this slightly penalizes it on short workloads where fixed pools are immediately ready.
- CPU load awareness (`OperatingSystemMXBean`) moderates scale-up under saturation instead of blocking it, preserving throughput under noisy neighbour conditions.
