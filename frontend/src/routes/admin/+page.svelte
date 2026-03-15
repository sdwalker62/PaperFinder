<script lang="ts">
    let { data } = $props();

    // Backfill form state
    let password = $state("");
    let lookbackDays = $state(7);
    let skipDelivery = $state(true);
    let loading = $state(false);
    let result = $state<{ ok: boolean; message: string } | null>(null);

    const { stats } = data;

    const dateRange = $derived(() => {
        if (!stats.oldest || !stats.newest) return "No data yet";
        const fmt = (iso: string) =>
            new Date(iso).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
            });
        return `${fmt(stats.oldest)} – ${fmt(stats.newest)}`;
    });

    const citationPct = $derived(
        stats.total > 0 ? Math.round((stats.withCitations / stats.total) * 100) : 0,
    );

    async function runPipeline(mode: "normal" | "backfill") {
        loading = true;
        result = null;

        try {
            const body: Record<string, unknown> = { password };
            if (mode === "backfill") {
                body.lookback_days = lookbackDays;
                body.skip_delivery = skipDelivery;
            }

            const res = await fetch("/api/pipeline", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });

            const data = await res.json();
            if (!res.ok) {
                result = { ok: false, message: data.message ?? `Error ${res.status}` };
            } else {
                result = {
                    ok: true,
                    message:
                        data.message ??
                        (mode === "backfill"
                            ? `Backfill triggered for ${lookbackDays} days — running in background`
                            : "Pipeline triggered — running in background"),
                };
            }
        } catch (err) {
            result = { ok: false, message: `Network error: ${(err as Error).message}` };
        } finally {
            loading = false;
            password = "";
        }
    }
</script>

<div class="max-w-2xl mx-auto flex flex-col gap-8">
    <!-- Page heading -->
    <div class="border-b border-base-content/20 pb-4">
        <h1
            class="text-2xl sm:text-3xl font-bold"
            style="font-family: 'Playfair Display', Georgia, serif;"
        >
            Admin Panel
        </h1>
        <p class="text-sm text-base-content/50 italic mt-0.5">
            Pipeline control and database management
        </p>
    </div>

    <!-- Stats -->
    <section>
        <h2
            class="text-[10px] tracking-widest uppercase text-base-content/40 mb-3"
        >
            Database
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-px bg-base-content/10 border border-base-content/10">
            {#each [
                { label: "Total Papers", value: stats.total.toLocaleString() },
                { label: "With Citations", value: `${stats.withCitations.toLocaleString()} (${citationPct}%)` },
                { label: "Date Range", value: dateRange() },
                { label: "Unenriched", value: (stats.total - stats.withCitations).toLocaleString() }
            ] as stat}
                <div class="bg-base-100 p-4">
                    <div class="text-[10px] tracking-widest uppercase text-base-content/40 mb-1">
                        {stat.label}
                    </div>
                    <div
                        class="text-lg font-semibold"
                        style="font-family: 'Playfair Display', Georgia, serif;"
                    >
                        {stat.value}
                    </div>
                </div>
            {/each}
        </div>
    </section>

    <!-- Result banner -->
    {#if result}
        <div
            class="border px-4 py-3 text-sm {result.ok
                ? 'border-base-content/20 text-base-content/70'
                : 'border-red-400/40 text-red-700 dark:text-red-400'}"
        >
            {result.message}
            <button
                class="ml-3 text-base-content/30 hover:text-base-content transition-colors"
                onclick={() => (result = null)}
            >
                ×
            </button>
        </div>
    {/if}

    <!-- Password (shared across both actions) -->
    <section>
        <h2 class="text-[10px] tracking-widest uppercase text-base-content/40 mb-3">
            Authentication
        </h2>
        <input
            type="password"
            placeholder="Admin password"
            bind:value={password}
            disabled={loading}
            autocomplete="off"
            class="w-full border border-base-content/20 bg-base-100 px-3 py-2 text-sm focus:outline-none focus:border-base-content/40"
        />
    </section>

    <!-- Run pipeline now -->
    <section class="border border-base-content/15 p-5">
        <h2
            class="text-base font-semibold mb-1"
            style="font-family: 'Playfair Display', Georgia, serif;"
        >
            Run Pipeline Now
        </h2>
        <p class="text-sm text-base-content/50 mb-4">
            Scrape today's sources, rank and summarise, enrich citations, then send the digest email.
        </p>
        <button
            onclick={() => runPipeline("normal")}
            disabled={loading || !password}
            class="border border-base-content/30 px-4 py-2 text-sm hover:bg-base-200 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
            {#if loading}
                Running…
            {:else}
                Run Pipeline
            {/if}
        </button>
    </section>

    <!-- Backfill -->
    <section class="border border-base-content/15 p-5">
        <h2
            class="text-base font-semibold mb-1"
            style="font-family: 'Playfair Display', Georgia, serif;"
        >
            Backfill
        </h2>
        <p class="text-sm text-base-content/50 mb-4">
            Re-run the pipeline looking further back in time. Useful for seeding the database.
            Existing papers are skipped automatically.
        </p>

        <div class="flex flex-col gap-4">
            <div>
                <label class="text-xs tracking-widest uppercase text-base-content/40 block mb-1.5">
                    Days to look back
                </label>
                <div class="flex items-center gap-3">
                    <input
                        type="range"
                        min="1"
                        max="90"
                        bind:value={lookbackDays}
                        disabled={loading}
                        class="flex-1 accent-current"
                    />
                    <span class="text-sm font-semibold w-16 text-right tabular-nums">
                        {lookbackDays} {lookbackDays === 1 ? "day" : "days"}
                    </span>
                </div>
            </div>

            <label class="flex items-center gap-2 text-sm cursor-pointer">
                <input
                    type="checkbox"
                    bind:checked={skipDelivery}
                    disabled={loading}
                    class="accent-current"
                />
                <span>Skip email &amp; Discord delivery</span>
                <span class="text-base-content/40 text-xs">(recommended for backfills)</span>
            </label>

            <div>
                <button
                    onclick={() => runPipeline("backfill")}
                    disabled={loading || !password}
                    class="border border-base-content/30 px-4 py-2 text-sm hover:bg-base-200 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    {#if loading}
                        Running…
                    {:else}
                        Backfill {lookbackDays} {lookbackDays === 1 ? "Day" : "Days"}
                    {/if}
                </button>
            </div>
        </div>
    </section>
</div>
