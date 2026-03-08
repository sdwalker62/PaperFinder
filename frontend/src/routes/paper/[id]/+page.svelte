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

<div class="flex flex-col gap-6">
    <!-- Back link -->
    <a
        href="/"
        class="inline-flex items-center gap-1 text-sm text-base-content/60 hover:text-base-content transition-colors w-fit"
    >
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
                d="M15 19l-7-7 7-7"
            />
        </svg>
        Back to feed
    </a>

    <!-- Paper detail -->
    <article class="prose prose-neutral dark:prose-invert prose-lg max-w-none">
        <div class="flex flex-wrap gap-2 not-prose mb-4">
            <span
                class="badge {paper.category === 'blog'
                    ? 'badge-secondary'
                    : 'badge-primary'} badge-sm"
            >
                {paper.category}
            </span>
            <span class="badge badge-outline badge-sm">
                {paper.sourceName}
            </span>
            <span class="text-sm text-base-content/60">{formattedDate}</span>
        </div>

        <h1 class="text-2xl sm:text-3xl font-bold leading-tight tracking-tight">
            {paper.title}
        </h1>

        {#if paper.topicsMatched.length > 0}
            <div class="flex flex-wrap gap-1.5 not-prose mt-4">
                {#each paper.topicsMatched as topic}
                    <span class="badge badge-ghost badge-sm">{topic}</span>
                {/each}
            </div>
        {/if}

        {#if paper.summary}
            <div class="mt-6">
                <h2 class="text-xl font-semibold">Summary</h2>
                <p class="text-base-content/60 whitespace-pre-line">
                    {paper.summary}
                </p>
            </div>
        {/if}

        {#if paper.abstract}
            <div class="mt-6">
                <h2 class="text-xl font-semibold">Abstract</h2>
                <p class="text-base-content/60 whitespace-pre-line">
                    {paper.abstract}
                </p>
            </div>
        {/if}

        <div class="not-prose mt-8">
            <a
                href={paper.url}
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-primary"
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
</div>
