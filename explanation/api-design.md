# API design explanation

## Overview

MEMORA exposes its domain model through a REST API implemented with Django REST Framework (DRF).

The API is not designed as a thin CRUD surface. It is designed as an exploration interface: it exposes relational structures (Piece, Designer, Era, Category, Maison) and supports query patterns that allow users to navigate the archive through relationships.

This document explains the intent behind the API design and the trade-offs it implies.

---

## Core principle: the API is a contract

The API acts as a stable contract between the backend and the frontend.

This enables:

- independent evolution of the Next.js exploration interface
- domain stability and integrity enforced by the backend
- predictable integration patterns for future clients (scripts, tools, import pipelines)

In practice, this means the API prioritises consistency and clarity over rapid, ad-hoc endpoint growth.

---

## Resource-oriented design

The API follows REST conventions by exposing domain entities as resources.

Core resources include:

- pieces
- designers
- eras
- categories
- maisons

Resources are represented as JSON and are accessible through list and detail endpoints.

This design keeps the domain model explicit and makes the API predictable for both humans and tooling.

---

## Relational retrieval as a first-class capability

Exploration requires relational context.

For that reason, the API supports retrieving entities together with key relationships (a Piece with its Designer and Era).

This makes relationships directly usable at the client level, without requiring multiple round-trops to reconstruct context.

Because relational retrieval can increase query cost, the backend is expected to apply ORM optimisation patterns (select_related / prefetch_related) as the dataset grows.

---

## Filtering as an exploration mechanism

Filtering is treated as a product capability, not a secondary convenience.

The API supports:

- filtering on direct attributes (text, dates, ranges)
- filtering on relationships (designer, era, category)
- filtering on editorial state (published/featured)
- filtering on quality signals (completeness)
- filtering on structured materials data (JSONField, PostgreSQL-dependent)

These query capabilities allow users to form combinatorial exploration paths rather than follow a single browsing hierarchy.

Detailed query parameters are documented in 'docs/references/filtering.md'.

---

## Publication and governance model

MEMORA enforces a read-public, write-restricted access model:

- read operations are public
- write operations are restricted to admin users

This aligns with the current beta governance approach:

- editorial curation occurs though Django Admin
- the frontend remains an exploration surface

This separation allows the archive to remain consistent while the product is still evolving.

---

## Completeness as an API-visible quality signal

The API exposes "completeness" as a filterable quality signal rather than a strict validation rule.

This supports archival reality: records evolve incrementally and can be enriched over time without blocking exploration.

Completeness criteria are documented and can evolve as the domain expands.

---

## Error handling and consistency

The API uses standard HTTP status codes and predictable JSON responses.

Consistency matters because the API is a contract. Breaking charges should be avoided or introduce intentionally with clear documentation.

As the system matures, this contract can support:

- semantic versioning of the API surface
- compatibility guarantees for clients
- automated validation via tests

---

## Summary

The MEMORA API is designed to expose the relational domain model in a way that supports exploration.

Its key characteristics are:

- contract-driven design (API-first)
- resource-oriented structure
- relational retrieval for context
- filtering as a core exploration mechanism
- clear governance via read-public / write-restricted permissions

The API design exists to serve the domain model and enable scalable exploration workflows.