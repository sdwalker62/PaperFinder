import { env } from '$env/dynamic/private';
import { PrismaPg } from '@prisma/adapter-pg';
import { PrismaClient } from '../../generated/prisma/client.ts';

function createPrismaClient() {
    const adapter = new PrismaPg({ connectionString: env.DATABASE_URL });
    return new PrismaClient({ adapter });
}

const prisma = globalThis.__prisma || createPrismaClient();

if (env.NODE_ENV !== 'production') {
    globalThis.__prisma = prisma;
}

export { prisma };
