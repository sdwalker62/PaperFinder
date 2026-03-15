<script lang="ts">
    interface Props {
        viewMonth: string; // "YYYY-MM"
        activeDates: string[];
        selectedDate: string | null;
        category: string | null;
    }

    let { viewMonth, activeDates, selectedDate, category }: Props = $props();

    const DOW_LABELS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

    const activeSet = $derived(new Set(activeDates));

    const parsed = $derived(viewMonth.split('-').map(Number) as [number, number]);

    const monthLabel = $derived(
        new Date(parsed[0], parsed[1] - 1, 1).toLocaleDateString('en-US', {
            month: 'long',
            year: 'numeric'
        })
    );

    const today = new Date().toISOString().split('T')[0];

    const cells = $derived(
        (() => {
            const [year, mon] = parsed;
            const firstDow = new Date(Date.UTC(year, mon - 1, 1)).getUTCDay();
            const daysInMonth = new Date(Date.UTC(year, mon, 0)).getUTCDate();
            const arr: (number | null)[] = [];
            for (let i = 0; i < firstDow; i++) arr.push(null);
            for (let d = 1; d <= daysInMonth; d++) arr.push(d);
            while (arr.length % 7 !== 0) arr.push(null);
            return arr;
        })()
    );

    function dateStr(day: number): string {
        const [year, mon] = parsed;
        return `${year}-${String(mon).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    }

    function monthStr(offsetMonths: number): string {
        const [year, mon] = parsed;
        const d = new Date(Date.UTC(year, mon - 1 + offsetMonths, 1));
        return `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, '0')}`;
    }

    function buildUrl(params: {
        month?: string;
        date?: string | null;
        category?: string | null;
        page?: number;
    }): string {
        const p = new URLSearchParams();
        if (params.month) p.set('month', params.month);
        if (params.date) p.set('date', params.date);
        if (params.category) p.set('category', params.category);
        if (params.page && params.page > 1) p.set('page', String(params.page));
        return '/?' + p.toString();
    }
</script>

<div class="text-sm select-none">
    <!-- Month header -->
    <div class="flex items-center justify-between mb-3">
        <a
            href={buildUrl({ month: monthStr(-1), category })}
            class="w-6 h-6 flex items-center justify-center hover:text-primary transition-colors text-base-content/40 hover:text-base-content"
            aria-label="Previous month"
        >
            ‹
        </a>
        <span
            class="text-xs font-semibold tracking-widest uppercase text-base-content/60"
            style="font-family: 'Playfair Display', Georgia, serif;"
        >
            {monthLabel}
        </span>
        <a
            href={buildUrl({ month: monthStr(1), category })}
            class="w-6 h-6 flex items-center justify-center hover:text-primary transition-colors text-base-content/40 hover:text-base-content"
            aria-label="Next month"
        >
            ›
        </a>
    </div>

    <!-- Day-of-week header -->
    <div class="grid grid-cols-7 mb-1">
        {#each DOW_LABELS as label}
            <div class="text-center text-[10px] tracking-widest uppercase text-base-content/30 pb-1">
                {label}
            </div>
        {/each}
    </div>

    <!-- Day cells -->
    <div class="grid grid-cols-7 gap-y-0.5">
        {#each cells as day}
            {#if day === null}
                <div></div>
            {:else}
                {@const ds = dateStr(day)}
                {@const isSelected = ds === selectedDate}
                {@const isToday = ds === today}
                {@const hasItems = activeSet.has(ds)}
                {@const href = isSelected
                    ? buildUrl({ month: viewMonth, category })
                    : buildUrl({ date: ds, month: viewMonth, category })}
                <a
                    {href}
                    class="relative flex flex-col items-center justify-center h-8 w-full transition-colors
                        {isSelected
                            ? 'bg-base-content text-base-100'
                            : isToday
                              ? 'text-primary font-bold hover:bg-base-200'
                              : hasItems
                                ? 'hover:bg-base-200 text-base-content'
                                : 'text-base-content/30 cursor-default pointer-events-none'}"
                >
                    <span class="text-xs leading-none">{day}</span>
                    {#if hasItems}
                        <span
                            class="absolute bottom-1 w-1 h-1 rounded-full
                                {isSelected ? 'bg-base-100' : 'bg-primary'}"
                        ></span>
                    {/if}
                </a>
            {/if}
        {/each}
    </div>
</div>
