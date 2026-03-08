<script lang="ts">
    import PipelineTrigger from "$lib/components/PipelineTrigger.svelte";
    import ThemeToggle from "$lib/components/ThemeToggle.svelte";
</script>

<header
    class="navbar sticky top-0 z-50 border-b border-base-300 bg-base-200/95 backdrop-blur"
>
    <div class="container mx-auto flex max-w-4xl items-center px-4">
        <a
            href="/"
            class="flex items-center gap-2 font-bold text-lg hover:opacity-80 transition-opacity"
        >
            <svg
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="2"
            >
                <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                />
            </svg>
            PaperFinder
        </a>
        <div class="ml-auto flex items-center gap-2">
            <PipelineTrigger />
            <ThemeToggle />
        </div>
    </div>
</header>
