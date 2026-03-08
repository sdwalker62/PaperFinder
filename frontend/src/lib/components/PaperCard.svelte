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

<div
    class="rounded-lg border border-border bg-card p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow"
>
    <div class="flex flex-wrap items-start gap-2">
        <span
            class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium {category ===
            'blog'
                ? 'bg-secondary text-secondary-foreground'
                : 'bg-primary text-primary-foreground'}"
        >
            {category}
        </span>
        <span
            class="inline-flex items-center rounded-full border border-border px-2.5 py-0.5 text-xs font-medium text-muted-foreground"
        >
            {sourceName}
        </span>
    </div>
    <h3 class="mt-2 text-base sm:text-lg font-semibold leading-snug">
        <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            class="hover:text-primary transition-colors underline-offset-4 hover:underline"
        >
            {title}
        </a>
    </h3>
    {#if summary}
        <p class="mt-2 text-sm text-muted-foreground line-clamp-3">{summary}</p>
    {/if}
    {#if topicsMatched.length > 0}
        <div class="flex flex-wrap gap-1.5 mt-3">
            {#each topicsMatched as topic}
                <span
                    class="inline-flex items-center rounded-md border border-border px-2 py-0.5 text-xs text-muted-foreground"
                >
                    {topic}
                </span>
            {/each}
        </div>
    {/if}
</div>
