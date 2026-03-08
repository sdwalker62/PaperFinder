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
    class="card bg-base-200 border border-base-300 p-4 sm:p-6 shadow-sm hover:shadow-md transition-shadow"
>
    <div class="flex flex-wrap items-start gap-2">
        <span
            class="badge {category === 'blog'
                ? 'badge-secondary'
                : 'badge-primary'} badge-sm"
        >
            {category}
        </span>
        <span class="badge badge-outline badge-sm">
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
        <p class="mt-2 text-sm text-base-content/60 line-clamp-3">{summary}</p>
    {/if}
    {#if topicsMatched.length > 0}
        <div class="flex flex-wrap gap-1.5 mt-3">
            {#each topicsMatched as topic}
                <span class="badge badge-ghost badge-sm">{topic}</span>
            {/each}
        </div>
    {/if}
</div>
