import { prisma } from '$lib/server/prisma';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
    const [total, withCitations, oldest, newest] = await Promise.all([
        prisma.paper.count(),
        prisma.paper.count({ where: { citationCount: { gt: 0 } } }),
        prisma.paper.findFirst({
            orderBy: { published: 'asc' },
            select: { published: true }
        }),
        prisma.paper.findFirst({
            orderBy: { published: 'desc' },
            select: { published: true }
        })
    ]);

    return {
        stats: {
            total,
            withCitations,
            oldest: oldest?.published?.toISOString() ?? null,
            newest: newest?.published?.toISOString() ?? null
        }
    };
};
