import { env } from '$env/dynamic/private';
import { error, json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
    const body = await request.json();
    const { password } = body as { password?: string };

    if (!env.ADMIN_PASSWORD) {
        throw error(500, 'ADMIN_PASSWORD not configured');
    }

    if (!password || password !== env.ADMIN_PASSWORD) {
        throw error(401, 'Invalid password');
    }

    const pipelineUrl = env.PIPELINE_URL;
    if (!pipelineUrl) {
        throw error(500, 'PIPELINE_URL not configured');
    }

    try {
        const response = await fetch(pipelineUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            signal: AbortSignal.timeout(300_000) // 5 minute timeout
        });

        if (!response.ok) {
            const text = await response.text();
            throw error(502, `Pipeline returned ${response.status}: ${text}`);
        }

        const result = await response.json();
        return json({ success: true, result });
    } catch (err) {
        if (err && typeof err === 'object' && 'status' in err) throw err;
        throw error(502, `Failed to reach pipeline: ${(err as Error).message}`);
    }
};
