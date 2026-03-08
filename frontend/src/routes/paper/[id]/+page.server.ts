import { prisma } from '$lib/server/prisma';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
    const paper = await prisma.paper.findUnique({
        where: { id: params.id }
    });

    if (!paper) {
        throw error(404, 'Paper not found');
    }

    return { paper };
};
