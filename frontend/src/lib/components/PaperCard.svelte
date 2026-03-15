<script lang="ts">
    interface Props {
        title: string;
        url: string;
        sourceName: string;
        category: string;
        summary: string;
        topicsMatched: string[];
    }

    let { title, url, sourceName, category, summary, topicsMatched }: Props =
        $props();
</script>

<div class="py-4 group">
    <div class="flex flex-wrap items-center gap-x-2 gap-y-1 mb-1.5">
        <span
            class="text-[10px] font-bold tracking-widest uppercase {category === 'blog'
                ? 'text-secondary'
                : 'text-primary'}"
        >
            {category}
        </span>
        <span class="text-base-content/30 text-xs">·</span>
        <span class="text-[10px] tracking-wider uppercase text-base-content/40">
            {sourceName}
        </span>
    </div>

    <h3
        class="text-base sm:text-lg font-semibold leading-snug"
        style="font-family: 'Playfair Display', Georgia, serif;"
    >
        <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-primary transition-colors underline-offset-4 group-hover:underline"
        >
            {title}
        </a>
    </h3>

    {#if summary}
        <p class="mt-1.5 text-sm text-base-content/60 leading-relaxed line-clamp-3 lg:line-clamp-none italic">
            {summary}
        </p>
    {/if}

    {#if topicsMatched.length > 0}
        <div class="flex flex-wrap gap-x-2 gap-y-1 mt-2">
            {#each topicsMatched as topic}
                <span class="text-[10px] tracking-wide uppercase text-base-content/40 border border-base-content/20 px-1.5 py-0.5">
                    {topic}
                </span>
            {/each}
        </div>
    {/if}
</div>
