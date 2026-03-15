<script lang="ts">
    import CalendarWidget from "$lib/components/CalendarWidget.svelte";
    import FeaturedCarousel from "$lib/components/FeaturedCarousel.svelte";
    import TimelineDay from "$lib/components/TimelineDay.svelte";

    let { data } = $props();

    const activeCategory = $derived(data.category);

    function buildUrl(overrides: Record<string, string | null | undefined>): string {
        const p = new URLSearchParams();
        const base: Record<string, string | null | undefined> = {
            category: data.category,
            date: data.selectedDate,
            month: data.viewMonth,
        };
        const merged = { ...base, ...overrides };
        for (const [k, v] of Object.entries(merged)) {
            if (v) p.set(k, v);
        }
        return '/?' + p.toString();
    }
</script>

<div class="grid grid-cols-1 md:grid-cols-[14rem_1fr] gap-8 items-start">
    <!-- Calendar sidebar -->
    <aside class="md:sticky md:top-8">
        <!-- Calendar label -->
        <div class="text-[10px] tracking-widest uppercase text-base-content/40 mb-3 border-b border-base-content/15 pb-2">
            Browse by Date
        </div>
        <CalendarWidget
            viewMonth={data.viewMonth}
            activeDates={data.activeDates}
            selectedDate={data.selectedDate}
            category={data.category}
        />
    </aside>

    <!-- Feed -->
    <div class="flex flex-col gap-6 min-w-0">
        <!-- Featured carousel -->
        <FeaturedCarousel papers={data.featuredPapers} />

        <!-- Header -->
        <div class="flex flex-col sm:flex-row sm:items-baseline justify-between gap-3 border-b border-base-content/20 pb-4">
            <div>
                <h1
                    class="text-2xl sm:text-3xl font-bold"
                    style="font-family: 'Playfair Display', Georgia, serif;"
                >
                    Latest Papers
                </h1>
                <p class="text-base-content/50 text-sm mt-0.5 italic">
                    {new Date().toLocaleDateString("en-US", {
                        weekday: "long",
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                    })}
                </p>
            </div>

            <!-- Category filter -->
            <div
                class="flex gap-0 text-sm border border-base-content/20 divide-x divide-base-content/20 self-start sm:self-auto"
            >
                <a
                    href={buildUrl({ category: null, page: null })}
                    class="px-3 py-1 transition-colors {!activeCategory
                        ? 'bg-base-content text-base-100'
                        : 'hover:bg-base-200'}"
                >
                    All
                </a>
                <a
                    href={buildUrl({ category: "paper", page: null })}
                    class="px-3 py-1 transition-colors {activeCategory === 'paper'
                        ? 'bg-base-content text-base-100'
                        : 'hover:bg-base-200'}"
                >
                    Papers
                </a>
                <a
                    href={buildUrl({ category: "blog", page: null })}
                    class="px-3 py-1 transition-colors {activeCategory === 'blog'
                        ? 'bg-base-content text-base-100'
                        : 'hover:bg-base-200'}"
                >
                    Blogs
                </a>
            </div>
        </div>

        <!-- Selected date banner -->
        {#if data.selectedDate}
            {@const label = new Date(data.selectedDate + 'T00:00:00').toLocaleDateString('en-US', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            })}
            <div class="flex items-center justify-between text-sm border border-base-content/20 px-3 py-2 bg-base-200">
                <span class="italic text-base-content/70">
                    Showing papers from <span class="font-medium not-italic">{label}</span>
                </span>
                <a
                    href={buildUrl({ date: null, page: null })}
                    class="text-base-content/40 hover:text-base-content transition-colors ml-4 text-xs tracking-widest uppercase"
                >
                    Clear ×
                </a>
            </div>
        {/if}

        <!-- Timeline -->
        {#if data.days.length > 0}
            <div class="flex flex-col divide-y divide-base-content/10">
                {#each data.days as day (day.date)}
                    <TimelineDay date={day.date} papers={day.papers} />
                {/each}
            </div>

            <!-- Pagination (hidden when a date is selected) -->
            {#if data.totalPages > 1 && !data.selectedDate}
                <div
                    class="flex justify-center items-center gap-4 mt-4 text-sm border-t border-base-content/20 pt-4"
                >
                    {#if data.page > 1}
                        <a
                            href={buildUrl({ page: String(data.page - 1) })}
                            class="hover:underline underline-offset-4"
                        >
                            ← Previous
                        </a>
                    {/if}
                    <span class="text-base-content/50 italic">
                        Page {data.page} of {data.totalPages}
                    </span>
                    {#if data.page < data.totalPages}
                        <a
                            href={buildUrl({ page: String(data.page + 1) })}
                            class="hover:underline underline-offset-4"
                        >
                            Next →
                        </a>
                    {/if}
                </div>
            {/if}
        {:else}
            <div
                class="flex flex-col items-center justify-center py-20 text-base-content/50 text-center"
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-14 w-14 mb-4 opacity-30"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="1"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
                    />
                </svg>
                <p
                    class="text-lg italic"
                    style="font-family: 'Playfair Display', Georgia, serif;"
                >
                    {data.selectedDate ? "No papers on this date" : "No papers yet"}
                </p>
                <p class="text-sm mt-1">
                    {data.selectedDate
                        ? "Try selecting another day from the calendar."
                        : "Papers will appear here once the pipeline runs."}
                </p>
            </div>
        {/if}
    </div>
</div>
