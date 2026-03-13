# Domain model explanation

## Overview

MEMORA is built around a relational domain model that treats relationships between entities as primary structure of exploration.

Rather than treating archival records as isolated objects, MEMORA models fashion archives as a network of interconnected entities. 

The domain model reflects the stucture of fashion creation itself, where each piece exists within a broader context of authorship, era, typology, and institutional affiliation.

---

## Core design principle: relational navigation

The central design principle of the MEMORA demain model is that relationships are not secondary metadata, but primary navigational structures.

In many archival systems, relationships are treated as descriptive attributes. In MEMORA, relationships define the structure through which uses explore the archive.

For example, a Piece is not only an object with attributes, but an entry point into a network of related entities:

- its Designer
- its Era
- its Category
- its Maison (indirectly, through the Designer)

Each of these relationships enables further exploration.

This relational structure transforms the archive from a static collection into an explorable knowledge system.

---

## Core entities

### Piece

Piece is the central entity of the domain model.

It represents an individual fashion object and serves as the primary entry point for exploration.

A Piece contains descriptive attributes (such as title, description, and materials) and relational attributes that connect it to other domain entities.

The Piece entity enables users to explore the archive starting from a concrete artifact.

### Designer

Designer represents the creator of one or more Pieces.

This entity enables exploration across authorship, allowing users to navigate from a Piece to other works by the same Designer.

Designers may also be associated with a Maison, enabling institutional exploration.

### Era

Era represents a historical context.

This entity enables chronological exploration and allows users to understand how Pieces relate to specific historical periods.

Eras provide temporal stucture to the archive.

### Category

Category represents typological classification.

This entity enables structural exploration across types of garments or objects.

Categories allow users to identify formal relationships between Pieces.

### Maison

Maison represents an institutional entity such as a fashion house.

This entity provides institutional context and enables exploration across organisational structures.

Maisons connect Designers and Pieces to broader institutional histories.

---

## Relational structure

The domain model is implemented as a relational graph, where entities are connected through explicit foreign key relationships.

Core relationships include:

- Piece → Designer
- Piece → Era
- Piece → Category
- Designer → Maison

These relationships enable multi-directional exploration.

For example, users can navigate:

- from a Piece to its Designer
- from a Designer to other Pieces
- from a Piece to its Era
- from an Era to other Pieces in the same period

This structure supports relational exploration workflows.

---

## Completeness as a domain concept

MEMORA treats completeness as a progressive quality signal rather than a strict validation requirement.

Archival records often evolve incrementally. Early records may contain partial information and be enriched over time.

The system allows incomplete records to exist while providing mechanisms to identify complete records.

This approach supports progressive archival enrichment while preserving usability.

---

## Alignment with system architecture

The domain model directly informas the system architecture.

The backend exposes domain entities through the API, preserving their relational structure.

The frontend uses this relational structure to enable exploration workflows.

Filtering, navigation, and exploration are all built upon the domain model.

The architecture exists to serve the domain model, not the reverse.

---

## Rationale for relational modelling

A relational model was chosen because it reflects the inherent structure of fashion archival knowledge.

Fashion objects exist within interconnected systems of authorship, history, and classification.

A relational model provides:

- structural clarity
- referential integrity
- efficient relational querying
- scalable exploration capabilities

Alternative models, such as document-based storage, would make relational exploration more complex and less explicit.

---

## Summary

The MEMORA domain model treats fashion archives as a relational knowledge system.

By modelling explicit entities and relationships, the system enables exploration, analysis, and creative discovery.

The domain model forms the conceptual and structural foundation of the entire system.