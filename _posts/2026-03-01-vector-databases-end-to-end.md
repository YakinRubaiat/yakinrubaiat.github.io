---
layout: post
title: Vector Databases, End to End
date: 2026-03-01 10:00:00-0800
description: A detailed guide to embeddings, similarity geometry, ANN indexing (HNSW/IVF/LSH/PQ), and production vector search design.
tags: [AI, vector-database, embeddings, ann-search, semantic-search, rag]
categories: [Technical]
math: true
giscus_comments: false
related_posts: false
---

## Why this topic was confusing at first

When I first encountered vector databases, I understood the words separately but not together. I already knew how ordinary databases work: store rows, build indexes, and run exact lookups or filtered queries. A vector database seemed like the same thing with a new name, and that made me skeptical.

The confusion disappeared once I accepted one key idea: semantic retrieval is not exact matching. It is geometric retrieval. Instead of asking for a row that exactly matches a string, we ask for items that are close in meaning. That means the system needs a representation of meaning and a fast way to search neighborhoods in that representation space.

This post is intentionally detailed. It covers embeddings, training logic, similarity metrics, ANN indexing methods, production pipeline design, and practical tuning decisions.

## Part I: Embeddings are learned coordinates of meaning

An embedding model turns an input into a fixed-length vector. In plain language, it maps text, image, or other content into a point in a high-dimensional space. If training is successful, semantically similar items are placed near one another, and semantically unrelated items are separated.

I originally thought embeddings were just compressed text, similar to a generic dimensionality reduction trick. That is only partially true. Embeddings are not simply compressed copies of raw features. They are learned coordinates shaped by the model objective. During training, the model learns which directions in space help separate or align meanings. That is why embeddings behave like a semantic map rather than a compressed archive.

The fixed embedding size (for example 384, 768, or 1024) is not accidental. It is a model design choice with systems consequences. Smaller vectors reduce storage and speed up similarity calculations, but they may blur fine semantic distinctions. Larger vectors often improve representational capacity but increase memory, network transfer, and compute costs across the entire stack.

## Part II: How models learn similarity instead of memorizing pairs

Most modern embedding systems are trained with contrastive behavior. The model is shown examples that should be close (positive pairs) and examples that should be separated (negative pairs). This can be done with supervised pairs, weak supervision, in-batch negatives, augmentation pairs, or multimodal matching.

The commonly used objective is often written as InfoNCE:

$$
L_i = -\log \frac{\exp(\mathrm{sim}(v_i,u_i)/\tau)}{\sum_j \exp(\mathrm{sim}(v_i,u_j)/\tau)}
$$

In that expression, `v_i` is the anchor, `u_i` is its positive match, and other `u_j` terms are negatives. The temperature `tau` controls how sharp the softmax decision is. Lower temperature makes the model punish close negatives more aggressively.

A useful intuition is force-based: positives pull together, negatives push apart. After many updates, the embedding space organizes into semantic neighborhoods. The model is not storing every sentence pair in memory. It is learning a continuous mapping function, which is why unseen but related sentences can still end up near each other.

To keep the numeric intuition concrete, imagine a tiny 2D toy example with unit vectors where the anchor is `a = (1, 0)`, the positive is `p = (0.96, 0.28)`, and two negatives are `n1 = (0, 1)` and `n2 = (-1, 0)`. The anchor has very high similarity with `p`, moderate similarity with `n1`, and very low similarity with `n2`. Plugging those into the objective gives a low loss value, meaning the model already ranks the positive clearly above negatives. In real models the vectors are hundreds of dimensions, but the same logic applies.

## Part III: Similarity metrics and why geometry matters

When vectors are available, retrieval quality depends on the metric. For text embeddings, cosine similarity is common:

$$
\mathrm{cos\_sim}(u,v) = \frac{u \cdot v}{\|u\|\|v\|}
$$

Cosine focuses on angle alignment. Euclidean distance (L2) considers absolute distance in space. If vectors are normalized to unit length, the two metrics become tightly related:

$$
\|u-v\|^2 = 2 - 2(u \cdot v)
$$

That identity is one reason normalization is so popular in semantic search pipelines.

At this point many people ask: if the metric is straightforward, why do we need a special database? The answer is scale. With one million vectors of dimension 768, brute-force retrieval requires scanning everything per query. Even with optimized kernels, this quickly becomes expensive under real latency SLOs and concurrent traffic.

There is also a high-dimensional effect to keep in mind. As dimensions grow, raw distances tend to concentrate and become less discriminative. Good retrieval performance therefore depends on a combination of representation quality, metric choice, normalization policy, and index structure.

![Cosine similarity geometry: two vectors with angle-based closeness.](/assets/img/vector-database/cosine-geometry-simulation.svg)

## Part IV: HNSW in detail

HNSW (Hierarchical Navigable Small World) is one of the most practical ANN methods today because it gives very strong recall-latency trade-offs for many workloads.

The structure is a layered graph. Upper layers are sparse and act like long-range routing shortcuts. Lower layers are denser and provide fine-grained local navigation. You can think of the top as highways and the bottom as neighborhood roads.

Insertion is incremental. A new vector is assigned a random maximum layer from an exponential-style distribution. Most nodes live only in lower layers, while a smaller number appear at higher layers. This preserves sparsity in upper levels and keeps global routing efficient.

During insertion, the algorithm starts from a known entry node at the top layer, greedily moves toward closer nodes, descends layer by layer, and finally builds local connections near the insertion point. Two parameters strongly influence behavior: `M` controls the maximum neighborhood degree, and `efConstruction` controls how deeply the build process explores candidates.

Query-time search is similar in spirit. The algorithm routes quickly through upper layers, then runs best-first exploration near the bottom. `efSearch` is the main quality-speed dial at inference time. Higher values usually improve recall but cost more latency.

HNSW is attractive for dynamic systems because inserts are straightforward and quality is strong without excessive tuning. The cost is memory overhead from graph links in addition to vector storage.

![HNSW simulation: layered graph descent and candidate refinement.](/assets/img/vector-database/hnsw-search-simulation.svg)

## Part V: IVF in detail

IVF (Inverted File Index) starts with coarse partitioning. It runs clustering (typically k-means) to create centroids and assigns each vector to the nearest centroid list. At query time, instead of scanning the full corpus, the system first finds the nearest centroids and probes only a subset of those lists.

Two parameters matter most. `nlist` controls how many coarse clusters are created. `nprobe` controls how many clusters are searched per query. With low `nprobe`, retrieval is fast but can miss neighbors across boundaries. Increasing `nprobe` usually improves recall while increasing latency.

A simple way to see the gain is by rough arithmetic. Suppose one million vectors are split into one thousand lists. If the query probes five lists, the candidate set is closer to thousands than millions. The index has converted global search into local search, then exact reranking is performed inside that smaller candidate set.

IVF is often preferred when the corpus is large and predictable, especially when combined with compression.

![IVF simulation: centroid partitioning and selective nprobe search.](/assets/img/vector-database/ivf-probe-simulation.svg)

## Part VI: LSH in detail

LSH (Locality Sensitive Hashing) uses randomized hashing that preserves neighborhood probability. Instead of learning clusters, it applies random hyperplanes to generate binary hash codes. For each hyperplane, the sign of the dot product defines one bit.

In plain form:

$$
h(v) = \mathrm{sign}(w \cdot v)
$$

Using multiple hyperplanes gives a bit-string. Similar vectors are more likely to collide in the same buckets. At query time, the system hashes the query, collects bucket candidates, and reranks candidates with the real metric.

LSH can be elegant and very fast for candidate generation, but in many modern semantic workloads it trails well-tuned HNSW or IVF on recall at comparable resource budgets. Still, it remains valuable conceptually and can be useful when simple probabilistic partitioning is sufficient.

## Part VII: PQ in detail

Product Quantization (PQ) is about compression first. It splits each high-dimensional vector into multiple sub-vectors, learns a small codebook for each subspace, and stores only code indices instead of full float values.

The memory impact can be dramatic. A 768-dimensional `float32` vector requires 3072 bytes in raw form. With subspace coding, storage can be reduced by orders of magnitude depending on configuration. This is why PQ is common in large-scale systems where RAM or VRAM is the real bottleneck.

PQ search usually works with lookup tables rather than full reconstruction. Distances are approximated by summing precomputed subspace contributions. This can be very efficient, especially when paired with a coarse index such as IVF, producing the widely used `IVF+PQ` design.

Compression always introduces approximation error, so tuning must evaluate quality loss against memory and throughput gains.

![PQ simulation: vector split, codebooks, and compressed-code lookup.](/assets/img/vector-database/pq-compression-simulation.svg)

## Part VIII: Putting everything together in a production pipeline

A practical retrieval request usually flows through these stages: query encoding, ANN candidate generation, metadata filtering, similarity reranking, and final top-k return. In RAG systems, the top documents then pass into chunk assembly and prompt construction before generation.

What matters in production is not only index quality in isolation. Real retrieval quality depends on data freshness, chunking strategy, metadata correctness, permissions boundaries, and the consistency between query embeddings and document embeddings.

Hybrid retrieval is often stronger than pure vector retrieval. Keyword methods capture exact tokens, codes, and identifiers that semantic models may smooth out. Vector retrieval captures conceptual relatedness and paraphrase robustness. Blending both signals usually improves reliability.

![Semantic search simulation: clustered embeddings, ANN candidates, and top-k results.](/assets/img/vector-database/vector-search-simulation.svg)

## Part IX: Evaluation and tuning without guesswork

A strong system needs both offline and online evaluation. Offline, teams usually track Recall@k, nDCG, latency distribution (not only average), build time, and index memory footprint. Online, product signals such as task success, click quality, answer grounding, and abandonment are essential because they reveal whether retrieval helps real users.

Tuning should always be workload-specific. HNSW tuning centers on `efSearch`, `M`, and memory budget. IVF tuning centers on `nlist` and `nprobe`. PQ tuning centers on subspace count, codebook size, and acceptable approximation error. The correct configuration is discovered through measured trade-offs, not copied defaults.

## Part X: Mistakes that make systems look good in tests and fail in production

The most common failure pattern is evaluation mismatch. Teams tune on tiny clean datasets and deploy on noisy heterogeneous corpora. Another frequent issue is embedding mismatch, where query and document vectors come from inconsistent models or preprocessing pipelines. Filtering design is another hidden source of failure: if ACL and tenancy rules are bolted on late, both relevance and safety can break.

It is also easy to over-optimize index parameters while ignoring upstream data quality. Chunking, deduplication, and metadata quality often produce larger gains than an extra point of ANN recall.

## Final takeaway

A vector database is not just a storage engine with a new data type. It is a full retrieval system that turns semantic meaning into geometry and then uses specialized indexing to search that geometry under strict performance constraints.

Once you see the system end to end, the topic becomes much less mysterious. Embeddings define the space, metrics define closeness, ANN defines efficiency, and evaluation defines trustworthiness.
