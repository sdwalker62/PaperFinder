<script lang="ts">
    import TimelineDay from "$lib/components/TimelineDay.svelte";

    let { data } = $props();

    const activeCategory = $derived(data.category);
</script>

<div class="flex flex-col gap-6">
    <!-- Header -->
    <div
        class="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
    >
        <div>
            <h1 class="text-2xl sm:text-3xl font-bold tracking-tight">
                Paper Feed
            </h1>
            <p class="text-base-content/60 text-sm mt-1">
                Latest AI/ML papers and blog posts
            </p>
        </div>

        <!-- Category filter -->
        <div class="join">
            <a
                href="/"
                class="btn btn-sm join-item {!activeCategory
                    ? 'btn-primary'
                    : 'btn-ghost'}"
            >
                All
            </a>
            <a
                href="/?category=paper"
                class="btn btn-sm join-item {activeCategory === 'paper'
                    ? 'btn-primary'
                    : 'btn-ghost'}"
            >
                Papers
            </a>
            <a
                href="/?category=blog"
                class="btn btn-sm join-item {activeCategory === 'blog'
                    ? 'btn-primary'
                    : 'btn-ghost'}"
            >
                Blogs
            </a>
        </div>
    </div>

    <!-- Timeline -->
    {#if data.days.length > 0}
        <div class="flex flex-col">
            {#each data.days as day (day.date)}
                <TimelineDay date={day.date} papers={day.papers} />
            {/each}
        </div>

        <!-- Pagination -->
        {#if data.totalPages > 1}
            <div class="flex justify-center items-center gap-2 mt-4">
                {#if data.page > 1}
                    <a
                        href="/?page={data.page - 1}{activeCategory
                            ? `&category=${activeCategory}`
                            : ''}"
                        class="btn btn-sm btn-ghost"
                    >
                        ← Previous
                    </a>
                {/if}
                <span class="text-sm text-base-content/60 px-3 py-1.5">
                    Page {data.page} of {data.totalPages}
                </span>
                {#if data.page < data.totalPages}
                    <a
                        href="/?page={data.page + 1}{activeCategory
                            ? `&category=${activeCategory}`
                            : ''}"
                        class="btn btn-sm btn-ghost"
                    >
                        Next →
                    </a>
                {/if}
            </div>
        {/if}
    {:else}
        <div
            class="flex flex-col items-center justify-center py-20 text-base-content/60"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-16 w-16 mb-4"
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
            <p class="text-lg font-medium">No papers found</p>
            <p class="text-sm">
                Papers will appear here once the pipeline runs.
            </p>
        </div>
    {/if}
</div>
