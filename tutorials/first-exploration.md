# Tutorial: First exploration of MEMORA

This tutorial introduces MEMORA as an exploration system.

By the end of this tutorial, you will be able to:

- explore archival Pieces
- navigate relational context (Designer, Era, Category)
- understand how relationships enable discovery

> This tutorial assumes MEMORA is running locally. If not, see 'docs/how-to/run-the-project.md'.

---

## Step 1: Open the exploration interface

Open your browser and go to:
http://localhost:3000/

You are now looking at the MEMORA frontend.

Navigate to:
/pieces

This page displays a list of archival Pieces.

Each Piece represents a fashion object connected to a broader relational context.

---

## Step 2: Open a Piece

Click on any Piece in the list.

You are now viewing a Piece detail page.

Observe the information displayed:

- title
- description
- designer
- era
- category

These fields describe the Piece, but theu also serve as entry points into the archives.

---

## Step 3: Explore relational context

The Designer, Era, and Category are not just descriptive fields. They represent relationships.

Each relationships connects this Piece to other Pieces.

For example:

- The Designer connects to other Pieces created by the same person
- The Era connects to Pieces from the same historical period
- The Category connects to Pieces of the same typology

These relationships form a navigational structure.

MEMORA uses this relational structure to enable exploration.

---

## Step 4: Understand relational exploration

Instead of browsing a fixed hierarchy, MEMORA allows exploration through relationships.

A Piece acts as an entry point into a network.

From a single Piece, you can conceptually navigate to:

- other Pieces by the same Designer
- other Pieces from the same Era
- other Pieces in the same Category

This structure reflects how fashion archives are naturally interconnected.

---

## Step 5: Observe the role of completeness

Some Pieces may have more information than others.

This reflects the nature of archival data, which evolves over time.

MEMORA allows incomplete records to exists while supporting progressive enrichment.

This enables exploration even when archival data is still being developed.

---

## Step 6: Understand the backend structure (optional)

The frontend retrieves data from the MEMORA API.

Example endpoint:
http://localhost:8000/api/pieces/

This API exposes the relational demain model that powers exploration.

See:

- 'docs/reference/api.md'
- 'docs/references/filtering.md'

for more details.

---

## What you learned

You have learned how MEMORA enables relational exploration.

Specifically, you have seen that:

- Pieces are connected to Designers, Eras, and Categories
- relationships enable exploration
- the archive is structured as a relational system, non a static collection

This relational structure is the foundation of MEMORA.