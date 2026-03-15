<script lang="ts">
    interface FeaturedPaper {
        id: string;
        title: string;
        url: string;
        sourceName: string;
        category: string;
        citationCount: number;
        relevanceScore: number;
        topicsMatched: string[];
        published: string | null;
    }

    interface Props {
        papers: FeaturedPaper[];
    }

    let { papers }: Props = $props();

    let scrollEl = $state<HTMLElement | undefined>(undefined);

    const hasCitations = $derived(papers.some((p) => p.citationCount > 0));

    function scroll(dir: -1 | 1) {
        if (!scrollEl) return;
        const card = scrollEl.querySelector("[data-card]") as HTMLElement | null;
        const width = card ? card.offsetWidth + 16 : 280;
        scrollEl.scrollBy({ left: dir * width * 2, behavior: "smooth" });
    }

    function formatCitations(n: number): string {
        if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
        return String(n);
    }
</script>

{#if papers.length > 0}
    <section class="mb-2">
        <!-- Section heading -->
        <div class="flex items-center justify-between mb-4 border-b border-base-content/20 pb-2">
            <div>
                <h2
                    class="text-lg sm:text-xl font-bold"
                    style="font-family: 'Playfair Display', Georgia, serif;"
                >
                    {hasCitations ? "Most Cited" : "Highly Relevant"}
                </h2>
                <p class="text-[10px] tracking-widest uppercase text-base-content/40 mt-0.5">
                    {hasCitations ? "All-time by citation count" : "Top-ranked by relevance"}
                </p>
            </div>
            <!-- Scroll arrows -->
            <div class="flex gap-1">
                <button
                    onclick={() => scroll(-1)}
                    class="w-7 h-7 flex items-center justify-center border border-base-content/20 hover:bg-base-200 transition-colors text-base-content/50 hover:text-base-content"
                    aria-label="Scroll left"
                >
                    ‹
                </button>
                <button
                    onclick={() => scroll(1)}
                    class="w-7 h-7 flex items-center justify-center border border-base-content/20 hover:bg-base-200 transition-colors text-base-content/50 hover:text-base-content"
                    aria-label="Scroll right"
                >
                    ›
                </button>
            </div>
        </div>

        <!-- Scrollable track -->
        <div
            bind:this={scrollEl}
            class="flex gap-4 overflow-x-auto pb-3 snap-x snap-mandatory scroll-smooth"
            style="scrollbar-width: none;"
        >
            {#each papers as paper (paper.id)}
                <a
                    href={paper.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    data-card
                    class="flex-none w-56 sm:w-64 lg:w-72 snap-start border border-base-content/15 bg-base-100 p-4 flex flex-col gap-2 hover:border-base-content/40 transition-colors group"
                >
                    <!-- Category + source -->
                    <div class="flex items-center gap-1.5">
                        <span
                            class="text-[9px] font-bold tracking-widest uppercase {paper.category === 'blog'
                                ? 'text-secondary'
                                : 'text-primary'}"
                        >
                            {paper.category}
                        </span>
                        <span class="text-base-content/20 text-[9px]">·</span>
                        <span class="text-[9px] tracking-wider uppercase text-base-content/35 truncate">
                            {paper.sourceName}
                        </span>
                    </div>

                    <!-- Title -->
                    <h3
                        class="text-sm font-semibold leading-snug line-clamp-3 group-hover:text-primary transition-colors"
                        style="font-family: 'Playfair Display', Georgia, serif;"
                    >
                        {paper.title}
                    </h3>

                    <!-- Spacer -->
                    <div class="flex-1"></div>

                    <!-- Footer: citation count or relevance -->
                    <div class="flex items-end justify-between mt-1">
                        {#if paper.citationCount > 0}
                            <div>
                                <div
                                    class="text-xl font-bold leading-none tabular-nums"
                                    style="font-family: 'Playfair Display', Georgia, serif;"
                                >
                                    {formatCitations(paper.citationCount)}
                                </div>
                                <div class="text-[9px] tracking-widest uppercase text-base-content/40 mt-0.5">
                                    citations
                                </div>
                            </div>
                        {:else}
                            <div>
                                <div
                                    class="text-xl font-bold leading-none tabular-nums"
                                    style="font-family: 'Playfair Display', Georgia, serif;"
                                >
                                    {Math.round(paper.relevanceScore * 100)}
                                </div>
                                <div class="text-[9px] tracking-widest uppercase text-base-content/40 mt-0.5">
                                    relevance
                                </div>
                            </div>
                        {/if}
                        {#if paper.published}
                            <div class="text-[9px] text-base-content/30 text-right">
                                {new Date(paper.published).toLocaleDateString("en-US", {
                                    month: "short",
                                    year: "numeric",
                                })}
                            </div>
                        {/if}
                    </div>
                </a>
            {/each}
        </div>
    </section>
{/if}
