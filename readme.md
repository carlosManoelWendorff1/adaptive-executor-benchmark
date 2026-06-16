# Adaptive Executor Benchmark

## Overview

This project evaluates different task execution strategies using Java and JMH (Java Microbenchmark Harness).

The goal is to compare the performance of multiple executor implementations under different workloads and system conditions.

Currently available executors:

- Sequential Executor
- Traditional Thread Pool Executor

Future implementations may include:

- Adaptive Executor
- Priority-based Executor
- Work-stealing Executor

---

## Project Structure

### Workloads

The benchmark simulates two different workload types:

#### Payment Tasks

Represents I/O-bound operations.

Simulation:

```text
Thread.sleep(...)
```

Configured through:

```properties
payment.sleep.ms=10
```

---

#### Analytics Tasks

Represents CPU-bound operations.

Simulation:

```text
Mathematical calculations executed in a loop
```

Configured through:

```properties
analytics.iterations=1000000
```

---

### Noise Generator

An optional CPU noise generator can be enabled to simulate a busy machine.

Configuration:

```properties
noise.enabled=true
noise.threads=8
```

When enabled, background threads continuously consume CPU resources during benchmark execution.

---

## Configuration

Benchmark workloads are configured in:

```text
src/main/resources/application.properties
```

Example:

```properties
# Workloads
workload.payments=2
workload.analytics=2

# Analytics simulation
analytics.iterations=1000000

# Payment simulation
payment.sleep.ms=10

# Noise
noise.enabled=true
noise.threads=8
```

---

## Building

Generate the benchmark JAR:

```bash
mvn clean package
```

Output:

```text
target/benchmarks.jar
```

---

## Running Benchmarks

Run all benchmarks:

```bash
java -jar target/benchmarks.jar ".*Benchmark.*"
```

---

### Recommended Execution

Generate CSV results:

```bash
java -jar target/benchmarks.jar ".*Benchmark.*" -rf csv -rff results.csv -wi 1 -i 10 -f 1
```

Parameters:

| Parameter | Description            |
| --------- | ---------------------- |
| -wi       | Warmup iterations      |
| -i        | Measurement iterations |
| -f        | Fork count             |
| -rf       | Result format          |
| -rff      | Output file            |

---

### Running a Single Benchmark

Sequential executor:

```bash
java -jar target/benchmarks.jar SequentialBenchmark
```

Traditional executor:

```bash
java -jar target/benchmarks.jar TraditionalBenchmark
```

---

## Output

Example CSV:

```csv
Benchmark,Mode,Score,Unit
SequentialBenchmark.execute,thrpt,32.91,ops/s
TraditionalBenchmark.execute,thrpt,92.84,ops/s
```

Higher throughput values indicate better performance.

---

## Notes

- JMH performs warmup iterations before measurements.
- Benchmark execution time depends on workload configuration.
- Results may vary depending on hardware, JVM version, operating system, and background CPU activity.
- For meaningful comparisons, use the same workload configuration across all executor implementations.

---

## Future Work

- Adaptive Executor implementation
- Dynamic worker scaling
- Priority scheduling
- Additional workload types
- Automated result visualization
- Statistical comparison of benchmark runs
