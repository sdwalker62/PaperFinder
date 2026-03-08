-- CreateTable
CREATE TABLE "papers" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "source_name" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "abstract" TEXT NOT NULL DEFAULT '',
    "published" TIMESTAMP(3),
    "summary" TEXT NOT NULL DEFAULT '',
    "relevance_score" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "topics_matched" TEXT[],
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "papers_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "papers_published_idx" ON "papers"("published");

-- CreateIndex
CREATE INDEX "papers_category_idx" ON "papers"("category");
