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

<div class="relative pl-8 sm:pl-12 pb-8 last:pb-0">
    <!-- Timeline line -->
    <div
        class="absolute left-3 sm:left-5 top-0 bottom-0 w-0.5 bg-base-300"
    ></div>

    <!-- Timeline dot -->
    <div
        class="absolute left-1.5 sm:left-3.5 top-1 w-4 h-4 rounded-full border-2 {isToday
            ? 'bg-primary border-primary'
            : 'bg-base-300 border-base-300'}"
    ></div>

    <!-- Day header -->
    <div class="mb-4">
        <h2 class="text-lg sm:text-xl font-bold">
            {#if isToday}
                <span class="text-primary">Today</span>
                <span class="text-base-content/60 text-sm font-normal ml-2"
                    >{formattedDate}</span
                >
            {:else}
                {formattedDate}
            {/if}
        </h2>
        <p class="text-sm text-base-content/60">
            {papers.length}
            {papers.length === 1 ? "paper" : "papers"}
        </p>
    </div>

    <!-- Paper list -->
    <div class="flex flex-col gap-3">
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
