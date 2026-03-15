<script lang="ts">
    import PipelineTrigger from "$lib/components/PipelineTrigger.svelte";
    import ThemeToggle from "$lib/components/ThemeToggle.svelte";
</script>

<header class="border-b-2 border-base-content/80 bg-base-100">
    <div class="container mx-auto max-w-4xl px-4">
        <!-- Top rule -->
        <div class="border-t border-base-content/20 mt-4"></div>

        <!-- Masthead row -->
        <div class="flex items-center justify-between py-3">
            <div class="text-xs text-base-content/50 tracking-widest uppercase hidden sm:block">
                Est. {new Date().getFullYear()}
            </div>

            <a href="/" class="text-center hover:opacity-80 transition-opacity">
                <div
                    class="text-3xl sm:text-5xl font-bold tracking-tight leading-none"
                    style="font-family: 'Playfair Display', Georgia, serif;"
                >
                    PaperFinder
                </div>
                <div class="text-xs tracking-[0.2em] uppercase text-base-content/50 mt-1">
                    Daily AI &amp; ML Digest
                </div>
            </a>

            <div class="flex items-center gap-1">
                <a
                    href="/admin"
                    class="btn btn-ghost btn-sm text-xs tracking-widest uppercase opacity-50 hover:opacity-100 transition-opacity hidden sm:flex"
                >
                    Admin
                </a>
                <PipelineTrigger />
                <ThemeToggle />
            </div>
        </div>

        <!-- Bottom rule -->
        <div class="border-t border-base-content/20 mb-0"></div>
    </div>
</header>
