import { env } from '$env/dynamic/private';
import { prisma } from '$lib/server/prisma';
import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ url }) => {
    const page = parseInt(url.searchParams.get('page') ?? '1', 10);
    const limit = parseInt(url.searchParams.get('limit') ?? '50', 10);
    const category = url.searchParams.get('category');
    const skip = (page - 1) * limit;

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

    return json({ papers, total, page, totalPages: Math.ceil(total / limit) });
};

export const POST: RequestHandler = async ({ request }) => {
    const apiKey = request.headers.get('x-api-key');
    if (!apiKey || apiKey !== env.API_KEY) {
        throw error(401, 'Unauthorized');
    }

    const body = await request.json();

    if (!Array.isArray(body)) {
        throw error(400, 'Request body must be an array of papers');
    }

    const created = await prisma.paper.createMany({
        data: body.map((p: Record<string, unknown>) => ({
            title: String(p.title ?? ''),
            url: String(p.url ?? ''),
            sourceName: String(p.source_name ?? ''),
            category: String(p.category ?? 'paper'),
            abstract: String(p.abstract ?? ''),
            published: p.published ? new Date(String(p.published)) : null,
            summary: String(p.summary ?? ''),
            relevanceScore: Number(p.relevance_score ?? 0),
            topicsMatched: Array.isArray(p.topics_matched) ? p.topics_matched.map(String) : []
        })),
        skipDuplicates: true
    });

    return json({ created: created.count }, { status: 201 });
};
