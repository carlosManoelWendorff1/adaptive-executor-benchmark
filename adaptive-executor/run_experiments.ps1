# run_experiments.ps1

$benchmarkJar = "target\benchmarks.jar"
$propsFile    = "src\main\resources\application.properties"
$resultsDir   = "results"

New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

$experiments = @(
    @{
        name = "01_baseline_low"
        props = @"
workload.payments=10
workload.analytics=10
workload.bursts=0
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=false
noise.threads=4
"@
    },
    @{
        name = "02_baseline_med"
        props = @"
workload.payments=100
workload.analytics=100
workload.bursts=0
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=false
noise.threads=4
"@
    },
    @{
        name = "03_baseline_high"
        props = @"
workload.payments=200
workload.analytics=200
workload.bursts=0
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=false
noise.threads=4
"@
    },
    @{
        name = "04_burst_low"
        props = @"
workload.payments=50
workload.analytics=50
workload.bursts=50
burst.iterations=2000000
burst.pause.ms=10
burst.count=2
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=false
noise.threads=4
"@
    },
    @{
        name = "05_burst_high"
        props = @"
workload.payments=50
workload.analytics=50
workload.bursts=100
burst.iterations=10000000
burst.pause.ms=5
burst.count=5
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=false
noise.threads=4
"@
    },
    @{
        name = "06_noise2_low"
        props = @"
workload.payments=100
workload.analytics=100
workload.bursts=0
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=true
noise.threads=2
"@
    },
    @{
        name = "07_noise2_burst"
        props = @"
workload.payments=50
workload.analytics=50
workload.bursts=50
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=true
noise.threads=2
"@
    },
    @{
        name = "08_noise4_low"
        props = @"
workload.payments=100
workload.analytics=100
workload.bursts=0
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=true
noise.threads=4
"@
    },
    @{
        name = "09_noise4_burst"
        props = @"
workload.payments=50
workload.analytics=50
workload.bursts=50
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=true
noise.threads=4
"@
    },
    @{
        name = "10_noise8_burst"
        props = @"
workload.payments=50
workload.analytics=50
workload.bursts=50
burst.iterations=5000000
burst.pause.ms=5
burst.count=3
executor.workers=2,4,8,16
analytics.iterations=100000000
payment.sleep.ms=10
noise.enabled=true
noise.threads=8
"@
    }
)

foreach ($exp in $experiments) {

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Experimento: $($exp.name)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # escreve o properties
    [System.IO.File]::WriteAllText(
    (Resolve-Path $propsFile),
    $exp.props,
    [System.Text.UTF8Encoding]::new($false))

    # recompila com o novo properties
    Write-Host "Compilando..." -ForegroundColor Yellow
    mvn clean package -q

    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO na compilacao de $($exp.name)" -ForegroundColor Red
        continue
    }

    # roda o benchmark
    $csvPath = "$resultsDir\$($exp.name).csv"
    Write-Host "Rodando benchmark -> $csvPath" -ForegroundColor Yellow

    java -jar $benchmarkJar ".*Benchmark.*" `
        -rf csv `
        -rff $csvPath `
        -wi 3 -i 5 -f 2

    Write-Host "Concluido: $($exp.name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Todos os experimentos concluidos. Resultados em: $resultsDir\" -ForegroundColor Green