import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

RESULTS_DIR = "results"
OUTPUT_DIR  = "charts"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── carrega todos os CSVs ──────────────────────────────────────────────────────

def load_results(results_dir):
    frames = []
    for path in sorted(glob.glob(f"{results_dir}/*.csv")):
        exp_name = os.path.basename(path).replace(".csv", "")
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.strip('"')
        df["experiment"] = exp_name
        frames.append(df)
    return pd.concat(frames, ignore_index=True)

def clean(df):
    df = df.copy()
    df["Benchmark"] = df["Benchmark"].str.strip('"').str.split(".").str[-2] \
    .str.replace("Benchmark", "", regex=False) \
    .str.strip()    
    # troca vírgula por ponto antes de converter
    df["Score"] = pd.to_numeric(
        df["Score"].astype(str).str.strip('"').str.replace(",", ".", regex=False),
        errors="coerce")
    df["Error"] = pd.to_numeric(
        df["Score Error (99,9%)"].astype(str).str.strip('"').str.replace(",", ".", regex=False),
        errors="coerce")
    
    df["workers"] = df["Param: workers"].apply(
        lambda x: "N/A" if pd.isna(x) else str(int(float(str(x).strip('"'))))
    )
    df["label"] = df.apply(
        lambda r: r["Benchmark"].replace("Benchmark", "").replace("execute", "").strip()
                  + (f" w={r['workers']}" if r["workers"] != "N/A" else ""),
        axis=1)
    return df

# ── paleta ─────────────────────────────────────────────────────────────────────

COLORS = {
    "Adaptive":        "#2563EB",
    "Sequential":      "#6B7280",
    "Traditional w=2": "#FCA5A5",
    "Traditional w=4": "#F87171",
    "Traditional w=8": "#EF4444",
    "Traditional w=16":"#B91C1C",
}

def color(label):
    for k, v in COLORS.items():
        if k.lower() in label.lower():
            return v
    return "#9CA3AF"

# ── gráfico 1: throughput por experimento (grouped bar) ───────────────────────

def chart_per_experiment(df):
    experiments = df["experiment"].unique()
    executors   = ["Adaptive", "Sequential",
                   "Traditional w=2", "Traditional w=4",
                   "Traditional w=8", "Traditional w=16"]

    fig, axes = plt.subplots(2, 5, figsize=(22, 9), sharey=False)
    axes = axes.flatten()

    for i, exp in enumerate(experiments):
        ax  = axes[i]
        sub = df[df["experiment"] == exp]

        scores = []
        errors = []
        labels = []
        colors = []

        for ex in executors:
            row = sub[sub["label"].str.contains(
                ex.replace(" ", "").lower(), case=False, regex=False)]
            if ex == "Adaptive":
                row = sub[sub["Benchmark"].str.lower() == "adaptive"]
            elif ex == "Sequential":
                row = sub[sub["Benchmark"].str.lower() == "sequential"]
            else:
                w   = ex.split("=")[1]
                row = sub[(sub["Benchmark"].str.lower() == "traditional") &
                          (sub["workers"] == w)]

            if row.empty:
                scores.append(0); errors.append(0)
            else:
                scores.append(row["Score"].values[0])
                errors.append(row["Error"].values[0]
                              if not np.isnan(row["Error"].values[0]) else 0)
            labels.append(ex)
            colors.append(color(ex))

        x    = np.arange(len(labels))
        bars = ax.bar(x, scores, yerr=errors, capsize=3,
                      color=colors, alpha=0.88, width=0.6,
                      error_kw={"elinewidth": 1, "ecolor": "#374151"})

        ax.set_title(exp.replace("_", " "), fontsize=9, fontweight="bold", pad=6)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
        ax.set_ylabel("ops/s", fontsize=8)
        ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.3f"))
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines[["top","right"]].set_visible(False)

    fig.suptitle("Throughput por experimento (ops/s)", fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/01_throughput_per_experiment.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {path}")

# ── gráfico 2: adaptive vs traditional w=16 ao longo dos cenários ─────────────

def chart_adaptive_vs_best_traditional(df):
    experiments = df["experiment"].unique()

    adapt_scores = []
    trad_scores  = []
    adapt_errors = []
    trad_errors  = []

    for exp in experiments:
        sub = df[df["experiment"] == exp]

        a = sub[sub["Benchmark"].str.lower() == "adaptive"]
        t = sub[(sub["Benchmark"].str.lower() == "traditional") & (sub["workers"] == "16")]

        adapt_scores.append(a["Score"].values[0]  if not a.empty else 0)
        adapt_errors.append(a["Error"].values[0]  if not a.empty and not np.isnan(a["Error"].values[0]) else 0)
        trad_scores.append(t["Score"].values[0]   if not t.empty else 0)
        trad_errors.append(t["Error"].values[0]   if not t.empty and not np.isnan(t["Error"].values[0]) else 0)

    x      = np.arange(len(experiments))
    width  = 0.35
    labels = [e.replace("_", "\n") for e in experiments]

    fig, ax = plt.subplots(figsize=(16, 6))
    ax.bar(x - width/2, adapt_scores, width, yerr=adapt_errors, capsize=3,
           label="Adaptive", color=COLORS["Adaptive"], alpha=0.88,
           error_kw={"elinewidth": 1})
    ax.bar(x + width/2, trad_scores,  width, yerr=trad_errors,  capsize=3,
           label="Traditional w=16", color=COLORS["Traditional w=16"], alpha=0.88,
           error_kw={"elinewidth": 1})

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("ops/s")
    ax.set_title("Adaptive vs Traditional w=16 — todos os cenários", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines[["top","right"]].set_visible(False)

    plt.tight_layout()
    path = f"{OUTPUT_DIR}/02_adaptive_vs_traditional16.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {path}")

# ── gráfico 3: degradação sob noise (linha) ───────────────────────────────────

def chart_noise_degradation(df):
    # experimentos com noise: 06,07,08,09,10
    noise_exps = [e for e in df["experiment"].unique()
                  if any(x in e for x in ["noise", "baseline_med"])]

    executors = {
        "Adaptive":         ("adaptive",     None),
        "Traditional w=2":  ("traditional",  "2"),
        "Traditional w=8":  ("traditional",  "8"),
        "Traditional w=16": ("traditional",  "16"),
        "Sequential":       ("sequential",   None),
    }

    fig, ax = plt.subplots(figsize=(13, 6))

    for label, (bench, workers) in executors.items():
        scores = []
        for exp in noise_exps:
            sub = df[df["experiment"] == exp]
            if workers:
                row = sub[(sub["Benchmark"].str.lower() == bench) &
                          (sub["workers"] == workers)]
            else:
                row = sub[sub["Benchmark"].str.lower() == bench]
            scores.append(row["Score"].values[0] if not row.empty else np.nan)

        ax.plot(noise_exps, scores, marker="o", label=label,
                color=color(label), linewidth=2)

    ax.set_xticklabels([e.replace("_", "\n") for e in noise_exps], fontsize=8)
    ax.set_xticks(range(len(noise_exps)))
    ax.set_ylabel("ops/s")
    ax.set_title("Degradação de throughput sob noise crescente", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(linestyle="--", alpha=0.4)
    ax.spines[["top","right"]].set_visible(False)

    plt.tight_layout()
    path = f"{OUTPUT_DIR}/03_noise_degradation.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {path}")

# ── gráfico 4: speedup do adaptive sobre sequential ───────────────────────────

def chart_speedup(df):
    experiments = df["experiment"].unique()
    speedups    = []

    for exp in experiments:
        sub  = df[df["experiment"] == exp]
        seq  = sub[sub["Benchmark"].str.lower() == "sequential"]["Score"]
        adap = sub[sub["Benchmark"].str.lower() == "adaptive"]["Score"]
        if not seq.empty and not adap.empty and seq.values[0] > 0:
            speedups.append(adap.values[0] / seq.values[0])
        else:
            speedups.append(0)

    x      = np.arange(len(experiments))
    labels = [e.replace("_", "\n") for e in experiments]

    fig, ax = plt.subplots(figsize=(14, 5))
    bars = ax.bar(x, speedups, color=COLORS["Adaptive"], alpha=0.85, width=0.6)
    ax.axhline(1, color="#6B7280", linestyle="--", linewidth=1, label="baseline (1x)")

    for bar, val in zip(bars, speedups):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f"{val:.1f}x", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Speedup (adaptive / sequential)")
    ax.set_title("Speedup do Adaptive sobre Sequential por cenário", fontweight="bold")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines[["top","right"]].set_visible(False)

    plt.tight_layout()
    path = f"{OUTPUT_DIR}/04_speedup_over_sequential.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {path}")

def chart_speedup_linear(df):
    experiments = df["experiment"].unique()
    worker_counts = [2, 4, 8, 16]
    worker_counts_plot = [1] + worker_counts  # [1, 2, 4, 8, 16]

    fig, axes = plt.subplots(2, 5, figsize=(22, 9), sharey=False)
    axes = axes.flatten()

    for i, exp in enumerate(experiments):
        ax  = axes[i]
        sub = df[df["experiment"] == exp]

        # baseline sequential
        seq_row = sub[sub["Benchmark"].str.lower() == "sequential"]
        if seq_row.empty or seq_row["Score"].values[0] == 0:
            continue
        seq_score = seq_row["Score"].values[0]

        # linha linear ideal — começa em (1,1)
        ax.plot(worker_counts_plot, worker_counts_plot,
                color="#000000", linewidth=1.2, linestyle="--",
                label="Linear (ideal)", zorder=5)

        # traditional — ponto (1, 1.0) como base + speedup por workers
        trad_speedups = [1.0]
        for w in worker_counts:
            row = sub[(sub["Benchmark"].str.lower() == "traditional") &
                      (sub["workers"] == str(w))]
            if not row.empty:
                trad_speedups.append(row["Score"].values[0] / seq_score)
            else:
                trad_speedups.append(np.nan)

        ax.plot(worker_counts_plot, trad_speedups,
                color="#EF4444", linewidth=1.8, linestyle="-.",
                marker="s", markersize=5,
                label="Traditional", zorder=4)

        # adaptive — linha horizontal com speedup atingido autonomamente
        adap_row = sub[sub["Benchmark"].str.lower() == "adaptive"]
        if not adap_row.empty:
            adap_speedup = adap_row["Score"].values[0] / seq_score

            ax.axhline(adap_speedup,
                       color="#2563EB", linewidth=1.8, linestyle=":",
                       label=f"Adaptive ({adap_speedup:.1f}x)", zorder=3)

            # marca onde adaptive ≈ traditional
            for j, ts in enumerate(trad_speedups):
                if ts is not np.nan and not np.isnan(ts) and abs(ts - adap_speedup) < 0.3:
                    ax.annotate("≈",
                                xy=(worker_counts_plot[j], ts),
                                fontsize=11, color="#2563EB",
                                ha="center", va="bottom")

        ax.set_title(exp.replace("_", " "), fontsize=9, fontweight="bold", pad=6)
        ax.set_xlabel("Workers (Traditional)", fontsize=8)
        ax.set_ylabel("Speedup vs Sequential", fontsize=8)
        ax.set_xticks(worker_counts_plot)
        ax.set_xlim(0.5, 18)
        ax.set_ylim(bottom=0.5)
        ax.legend(fontsize=7, loc="upper left")
        ax.grid(linestyle="--", alpha=0.4)
        ax.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Speedup vs Linear Ideal — por experimento",
                 fontsize=13, fontweight="bold", y=1.01)
    plt.tight_layout()
    path = f"{OUTPUT_DIR}/05_speedup_linear.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Salvo: {path}")

def export_summary_table(df):
    experiments = df["experiment"].unique()
    worker_counts = ["2", "4", "8", "16"]
    rows = []

    for exp in experiments:
        sub = df[df["experiment"] == exp]

        seq_row  = sub[sub["Benchmark"].str.lower() == "sequential"]
        adap_row = sub[sub["Benchmark"].str.lower() == "adaptive"]
        seq_score  = seq_row["Score"].values[0]  if not seq_row.empty  else np.nan
        adap_score = adap_row["Score"].values[0] if not adap_row.empty else np.nan

        row = {"experimento": exp, "sequential": seq_score, "adaptive": adap_score}

        for w in worker_counts:
            t = sub[(sub["Benchmark"].str.lower() == "traditional") &
                    (sub["workers"] == w)]
            row[f"traditional_w{w}"] = t["Score"].values[0] if not t.empty else np.nan

        # speedup adaptive vs melhor traditional
        best_trad = max(
            [row[f"traditional_w{w}"] for w in worker_counts
             if not np.isnan(row[f"traditional_w{w}"])],
            default=np.nan)
        row["best_traditional"] = best_trad
        row["adaptive_vs_best_%"] = round(
            (adap_score / best_trad - 1) * 100, 1) if not np.isnan(best_trad) else np.nan

        rows.append(row)

    summary = pd.DataFrame(rows)
    path = f"{OUTPUT_DIR}/summary.csv"
    summary.to_csv(path, index=False, float_format="%.4f")
    print(f"Salvo: {path}")

    # imprime no terminal também
    print("\n=== RESUMO ===")
    print(summary[["experimento", "sequential", "adaptive",
                    "best_traditional", "adaptive_vs_best_%"]].to_string(index=False))

# ── main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    raw = load_results(RESULTS_DIR)
    df  = clean(raw)
    
    # debug — remove depois
    print(df[["Benchmark", "Score", "workers", "experiment"]].to_string())
    chart_per_experiment(df)
    chart_adaptive_vs_best_traditional(df)
    chart_noise_degradation(df)
    chart_speedup(df)
    chart_speedup_linear(df)
    export_summary_table(df)

    print("\nPronto! Graficos salvos em:", OUTPUT_DIR)