import { prisma } from '$lib/server/prisma';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
    const page = parseInt(url.searchParams.get('page') ?? '1', 10);
    const limit = 50;
    const skip = (page - 1) * limit;
    const category = url.searchParams.get('category');

    const where = category ? { category } : {};

    const [papers, total] = await Promise.all([
        prisma.paper.findMany({
            where,
            orderBy: { published: 'desc' },
            skip,
            take: limit
        }),
        prisma.paper.count({ where })
    ]);

    // Group papers by date
    const grouped: Record<string, typeof papers> = {};
    for (const paper of papers) {
        const dateKey = paper.published
            ? paper.published.toISOString().split('T')[0]
            : paper.createdAt.toISOString().split('T')[0];
        if (!grouped[dateKey]) {
            grouped[dateKey] = [];
        }
        grouped[dateKey].push(paper);
    }

    // Sort dates descending
    const days = Object.entries(grouped)
        .sort(([a], [b]) => b.localeCompare(a))
        .map(([date, papers]) => ({ date, papers }));

    return {
        days,
        page,
        totalPages: Math.ceil(total / limit),
        category
    };
};
