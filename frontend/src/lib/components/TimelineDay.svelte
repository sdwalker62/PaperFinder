<script lang="ts">
    import PaperCard from "./PaperCard.svelte";

    interface Paper {
        id: string;
        title: string;
        url: string;
        sourceName: string;
        category: string;
        summary: string;
        topicsMatched: string[];
    }

    interface Props {
        date: string;
        papers: Paper[];
    }

    let { date, papers }: Props = $props();

    const formattedDate = $derived(
        new Date(date + "T00:00:00").toLocaleDateString("en-US", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric",
        }),
    );

    const isToday = $derived(
        (() => {
            const today = new Date().toISOString().split("T")[0];
            return date === today;
        })(),
    );
</script>

<div class="py-6">
    <!-- Day header -->
    <div class="mb-4 flex items-baseline gap-3">
        <h2
            class="text-base font-semibold tracking-wide uppercase text-base-content/50 text-xs"
        >
            {#if isToday}
                <span class="text-primary font-bold">Today</span>
                <span class="ml-2 font-normal normal-case tracking-normal text-base-content/40">{formattedDate}</span>
            {:else}
                {formattedDate}
            {/if}
        </h2>
        <div class="flex-1 border-t border-base-content/15"></div>
        <span class="text-xs text-base-content/40 italic">
            {papers.length} {papers.length === 1 ? "item" : "items"}
        </span>
    </div>

    <!-- Paper list -->
    <div class="flex flex-col divide-y divide-base-content/10">
        {#each papers as paper (paper.id)}
            <PaperCard
                title={paper.title}
                url={paper.url}
                sourceName={paper.sourceName}
                category={paper.category}
                summary={paper.summary}
                topicsMatched={paper.topicsMatched}
            />
        {/each}
    </div>
</div>
