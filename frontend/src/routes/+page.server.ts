import { prisma } from '$lib/server/prisma';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
    const page = parseInt(url.searchParams.get('page') ?? '1', 10);
    const limit = 50;
    const skip = (page - 1) * limit;
    const category = url.searchParams.get('category');
    const selectedDate = url.searchParams.get('date'); // YYYY-MM-DD

    // Determine which month the calendar should display
    const viewMonth = url.searchParams.get('month')
        ?? selectedDate?.slice(0, 7)
        ?? new Date().toISOString().slice(0, 7); // YYYY-MM

    const categoryWhere = category ? { category } : {};

    // When a date is selected, filter to that UTC day
    const dateWhere = selectedDate
        ? {
              published: {
                  gte: new Date(selectedDate + 'T00:00:00.000Z'),
                  lt: new Date(selectedDate + 'T24:00:00.000Z')
              }
          }
        : {};

    const where = { ...categoryWhere, ...dateWhere };

    // Parse viewMonth into UTC month boundaries for the active-dates query
    const [vmYear, vmMon] = viewMonth.split('-').map(Number);
    const monthStart = new Date(Date.UTC(vmYear, vmMon - 1, 1));
    const monthEnd = new Date(Date.UTC(vmYear, vmMon, 1));

    const [papers, total, publishedInMonth] = await Promise.all([
        prisma.paper.findMany({
            where,
            orderBy: { published: 'desc' },
            skip: selectedDate ? 0 : skip,
            take: selectedDate ? 200 : limit
        }),
        prisma.paper.count({ where }),
        // Lightweight query: just the published timestamps in this calendar month
        prisma.paper.findMany({
            where: {
                ...categoryWhere,
                published: { gte: monthStart, lt: monthEnd }
            },
            select: { published: true }
        })
    ]);

    // Deduplicate to a list of YYYY-MM-DD strings
    const activeDates = [
        ...new Set(
            publishedInMonth
                .filter((p) => p.published != null)
                .map((p) => p.published!.toISOString().split('T')[0])
        )
    ];

    // Group papers by date
    const grouped: Record<string, typeof papers> = {};
    for (const paper of papers) {
        const dateKey = paper.published
            ? paper.published.toISOString().split('T')[0]
            : paper.createdAt.toISOString().split('T')[0];
        if (!grouped[dateKey]) grouped[dateKey] = [];
        grouped[dateKey].push(paper);
    }

    const days = Object.entries(grouped)
        .sort(([a], [b]) => b.localeCompare(a))
        .map(([date, papers]) => ({ date, papers }));

    return {
        days,
        page,
        totalPages: Math.ceil(total / limit),
        category,
        selectedDate,
        viewMonth,
        activeDates
    };
};
