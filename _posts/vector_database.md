---
layout: post
title: Understanding Vector Databases
date: 2026-03-01 10:00:00-0800
description: A clean, practical guide to embeddings, similarity, ANN indexing, and production trade-offs.
tags: [Machine Learning, Databases, Search]
categories: [Technical]
giscus_comments: false
related_posts: false
---

## Understanding Vector Databases

When I first heard the term *vector database*, I understood regular databases but not why vectors needed their own system. The turning point was realizing that modern retrieval is less about exact string matching and more about finding items with similar meaning.

This post explains that idea from the ground up:
- what embeddings are,
- how similarity is measured,
- why brute-force search fails at scale,
- and how indexes like HNSW, IVF, LSH, and PQ make semantic search practical.

## 1) Why Vector Databases Exist

A traditional database works best when queries are exact:
- `id = 42`
- `country = 'USA'`
- `name LIKE '%coffee%'`

Semantic search asks a different question:
> “Find items that mean something similar to this query.”

To answer that, we convert text, images, or audio into vectors (embeddings). Once data becomes vectors, retrieval becomes a nearest-neighbor problem in high-dimensional space.

That is the core purpose of a vector database:  
**store embeddings and retrieve nearest neighbors quickly.**

## 2) Embeddings: Meaning as Coordinates

An embedding model maps an input \(x\) to a vector:
\[
f_\theta(x) = z \in \mathbb{R}^d
\]

The model is trained so semantically similar inputs land close together and unrelated inputs land farther apart.

### Not Compression in the PCA Sense

A common confusion is treating embeddings as simple compression. They are not just lower-dimensional copies of raw data. They are *learned coordinates* shaped by training objectives (contrastive loss, next-token prediction, etc.).

### Why Dimension Is Fixed

Embedding size (for example, 384, 768, 1024) is a design choice made during model training:
- higher dimension can represent more nuance,
- but costs more memory and compute.

So dimension is a trade-off, not a random number.

## 3) Measuring Similarity

Once everything is a vector, we need a similarity metric.

### Cosine Similarity
\[
\text{cos\_sim}(u,v) = \frac{u \cdot v}{\|u\| \|v\|}
\]

- Measures angle (direction).
- Common for text embeddings.
- Often used with normalized vectors.

### Euclidean (L2) Distance
\[
\text{L2}(u,v) = \sqrt{\sum_i (u_i - v_i)^2}
\]

- Measures straight-line distance.
- Sensitive to both magnitude and direction.

In many text retrieval systems, cosine similarity is the default because direction aligns well with semantic meaning.

## 4) Why Brute Force Breaks

Suppose you have \(N = 1{,}000{,}000\) vectors, each 768-dimensional. A brute-force top-\(k\) search compares the query with all \(N\) vectors every time:
\[
O(N)
\]

It is exact, but too expensive for low-latency production traffic.

So real systems use **Approximate Nearest Neighbor (ANN)** indexes: slightly approximate results for large speed gains.

## 5) Main ANN Indexing Methods

The methods below solve the same problem in different ways.

### HNSW (Hierarchical Navigable Small World)

HNSW builds a multi-layer graph:
- sparse upper layers for fast global routing,
- dense lower layer for local refinement.

Search starts at the top and greedily descends to promising regions.

Important parameters:
- `M`: max neighbors per node (memory/quality trade-off),
- `efConstruction`: build-time exploration,
- `efSearch`: query-time exploration.

Strengths: very strong recall and latency.  
Cost: higher memory usage.

### IVF (Inverted File Index)

IVF partitions vectors into clusters using k-means:
1. learn centroids (`nlist`),
2. assign each vector to its nearest centroid,
3. at query time, probe only a few clusters (`nprobe`).

Strength: efficient and tunable.  
Cost: quality depends on clustering and probe depth.

### LSH (Locality Sensitive Hashing)

LSH uses random hyperplanes to create hash codes:
- each hyperplane contributes one bit,
- similar vectors have similar bit patterns with high probability.

Query flow:
1. hash the query,
2. collect candidates from matching/nearby buckets,
3. rerank by real vector distance.

Strength: very fast candidate generation.  
Cost: usually lower recall than HNSW for the same resource budget.

### PQ (Product Quantization)

PQ is primarily compression:
1. split each vector into subspaces,
2. quantize each subspace with a small codebook,
3. store short integer codes instead of full floats.

This can shrink memory dramatically and allows fast approximate distance via lookup tables.

PQ is often combined with IVF (`IVF+PQ`) in large deployments.

![Vector database simulation: semantic clusters, query routing, and nearest-neighbor retrieval.](/assets/img/vector-database/vector-search-simulation.svg)

## 6) End-to-End Vector Search Pipeline

A production query usually looks like this:

1. **Encode query** into an embedding.
2. **Run ANN index** to get candidate neighbors.
3. **Compute exact similarity** on candidates.
4. **Apply metadata filters** (tenant, time, permissions, tags).
5. **Return top-\(k\)** results.

In RAG systems, this is followed by context assembly and generation.

## 7) Choosing the Right Strategy

| Situation | Good default |
|---|---|
| Need high recall + low latency | HNSW |
| Very large corpus, balanced budget | IVF |
| Memory-constrained at massive scale | IVF + PQ |
| Simple probabilistic baseline | LSH |
| Small corpus (< 100k vectors) | Brute force can be enough |

There is no universally best index. The right choice depends on:
- latency SLO,
- recall target,
- memory budget,
- update frequency,
- vector dimension and metric.

## 8) Practical Pitfalls

1. **Mixing embedding models**  
   Query and document vectors must come from compatible models.

2. **Skipping normalization**  
   If you rely on cosine similarity, normalize consistently.

3. **Ignoring filters early**  
   Hybrid retrieval quality drops if metadata filtering happens too late.

4. **No evaluation loop**  
   Track recall@k, latency p95/p99, and downstream answer quality.

5. **Overfitting index parameters**  
   Tune with realistic workloads, not tiny synthetic tests.

## 9) Final Takeaway

A vector database is not just storage. It is a retrieval system designed for semantic geometry.

- Embeddings turn meaning into coordinates.
- Similarity metrics define closeness.
- ANN indexes make retrieval fast enough for real products.
- The best system balances speed, memory, and accuracy for your workload.

That perspective is what made vector databases finally click for me.

## Short Glossary

| Term | Meaning |
|---|---|
| Embedding | Vector representation of semantic information |
| ANN | Approximate nearest neighbor search |
| HNSW | Graph-based ANN index with layered navigation |
| IVF | Cluster-based index with inverted lists |
| LSH | Hash-based approximate candidate retrieval |
| PQ | Quantization method for vector compression |
| Recall@k | Fraction of true neighbors captured in top-\(k\) |
| Top-\(k\) | Final highest-scoring retrieved items |
