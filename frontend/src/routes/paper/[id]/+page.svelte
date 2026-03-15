<script lang="ts">
    let { data } = $props();
    const paper = $derived(data.paper);

    const formattedDate = $derived(
        paper.published
            ? new Date(paper.published).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
              })
            : "Unknown date",
    );
</script>

<svelte:head>
    <title>{paper.title} — PaperFinder</title>
</svelte:head>

<!-- Back link -->
<a
    href="/"
    class="inline-flex items-center gap-1 text-sm text-base-content/50 hover:text-base-content transition-colors mb-6"
>
    <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        stroke-width="2"
    >
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
    </svg>
    Back to feed
</a>

<div class="grid grid-cols-1 lg:grid-cols-[1fr_16rem] gap-10 lg:gap-16 items-start">
    <!-- Main article -->
    <article class="flex flex-col gap-6 min-w-0">
        <!-- Category + source + date -->
        <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-[10px] tracking-widest uppercase text-base-content/40 border-b border-base-content/15 pb-4">
            <span class="{paper.category === 'blog' ? 'text-secondary' : 'text-primary'} font-bold">
                {paper.category}
            </span>
            <span class="text-base-content/20">·</span>
            <span>{paper.sourceName}</span>
            <span class="text-base-content/20">·</span>
            <span class="normal-case tracking-normal">{formattedDate}</span>
        </div>

        <!-- Title -->
        <h1
            class="text-2xl sm:text-3xl lg:text-4xl font-bold leading-tight"
            style="font-family: 'Playfair Display', Georgia, serif;"
        >
            {paper.title}
        </h1>

        <!-- Topics -->
        {#if paper.topicsMatched.length > 0}
            <div class="flex flex-wrap gap-x-2 gap-y-1">
                {#each paper.topicsMatched as topic}
                    <span class="text-[10px] tracking-wide uppercase text-base-content/40 border border-base-content/20 px-1.5 py-0.5">
                        {topic}
                    </span>
                {/each}
            </div>
        {/if}

        <!-- Summary -->
        {#if paper.summary}
            <div class="border-t border-base-content/10 pt-5">
                <h2
                    class="text-[10px] tracking-widest uppercase text-base-content/40 mb-3"
                >
                    Summary
                </h2>
                <p class="text-base leading-relaxed text-base-content/80 whitespace-pre-line italic">
                    {paper.summary}
                </p>
            </div>
        {/if}

        <!-- Abstract -->
        {#if paper.abstract}
            <div class="border-t border-base-content/10 pt-5">
                <h2
                    class="text-[10px] tracking-widest uppercase text-base-content/40 mb-3"
                >
                    Abstract
                </h2>
                <p class="text-sm leading-relaxed text-base-content/60 whitespace-pre-line">
                    {paper.abstract}
                </p>
            </div>
        {/if}

        <!-- Read link -->
        <div class="border-t border-base-content/15 pt-5">
            <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-2 border border-base-content/30 px-4 py-2 text-sm hover:bg-base-200 transition-colors"
            >
                Read full {paper.category === "blog" ? "post" : "paper"}
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    class="h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                    />
                </svg>
            </a>
        </div>
    </article>

    <!-- Desktop sidebar: metadata -->
    <aside class="hidden lg:flex flex-col gap-5 lg:sticky lg:top-8 text-sm">
        <div class="border-t-2 border-base-content/60 pt-4 flex flex-col gap-4">
            {#each [
                { label: "Source", value: paper.sourceName },
                { label: "Category", value: paper.category },
                { label: "Published", value: formattedDate },
                ...(paper.relevanceScore ? [{ label: "Relevance", value: `${Math.round(paper.relevanceScore * 100)}%` }] : []),
                ...(paper.citationCount ? [{ label: "Citations", value: paper.citationCount.toLocaleString() }] : [])
            ] as row}
                <div>
                    <div class="text-[10px] tracking-widest uppercase text-base-content/40 mb-0.5">
                        {row.label}
                    </div>
                    <div class="text-base-content/70 capitalize">{row.value}</div>
                </div>
            {/each}
        </div>
    </aside>
</div>
