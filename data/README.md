# Data

`legal_sources/` contains English and Spanish PDFs, `sources.json` (source
metadata), and `chunks.json` (extracted passages used by BM25 retrieval).
Keep source IDs and page references intact when rebuilding the index.

See the [architecture map](../docs/architecture.md#know-your-rights) for how
the corpus fits into the app and the [testing plan](../docs/testing-plan.md)
for proposed evaluation. Keep private recordings and large evaluation
datasets outside Git.
