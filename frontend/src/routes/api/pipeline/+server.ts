import { env } from '$env/dynamic/private';
import { error, json } from '@sveltejs/kit';
import aws4 from 'aws4';
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

    if (!env.PIPELINE_AWS_ACCESS_KEY_ID || !env.PIPELINE_AWS_SECRET_ACCESS_KEY) {
        throw error(500, 'AWS credentials not configured');
    }

    const url = new URL(pipelineUrl);
    const requestBody = JSON.stringify({});

    const opts = aws4.sign(
        {
            host: url.hostname,
            path: url.pathname,
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: requestBody,
            service: 'lambda',
            region: env.PIPELINE_AWS_REGION ?? 'us-east-1'
        },
        {
            accessKeyId: env.PIPELINE_AWS_ACCESS_KEY_ID,
            secretAccessKey: env.PIPELINE_AWS_SECRET_ACCESS_KEY,
            ...(env.PIPELINE_AWS_SESSION_TOKEN ? { sessionToken: env.PIPELINE_AWS_SESSION_TOKEN } : {})
        }
    );

    // Use an 8-second timeout so we respond before Netlify's 10s function limit.
    // Lambda continues running in the background regardless of client disconnect.
    try {
        const response = await fetch(pipelineUrl, {
            method: 'POST',
            headers: opts.headers as Record<string, string>,
            body: requestBody,
            signal: AbortSignal.timeout(8_000)
        });

        if (!response.ok) {
            const text = await response.text();
            throw error(502, `Pipeline returned ${response.status}: ${text}`);
        }

        const result = await response.json();
        return json({ success: true, result });
    } catch (err) {
        // If the 8s timeout fired, the request was sent and Lambda is processing
        if (err instanceof Error && err.name === 'TimeoutError') {
            return json({ success: true, message: 'Pipeline triggered — running in background' });
        }
        if (err && typeof err === 'object' && 'status' in err) throw err;
        throw error(502, `Failed to reach pipeline: ${(err as Error).message}`);
    }
};
