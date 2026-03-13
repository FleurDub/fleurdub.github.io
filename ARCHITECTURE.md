# MEMORA - Architecture Overview

## 1. Purpose and scope

MEMORA is a creative exploration system built upon structured fashion archival data.

It reconceives archives as a relational knowledge system, where relationships between entities (Piece, Designer, Era, Category, Maison).

The system exposes archival knowledge through a structured relational model and a REST API designed to support relational exploration, analysis, and creative workflows.

### Current scope (beta)

The current beta validates the core architectural approach:

- relational domain modelling
- API-based relational exploration
- editorial control via Django Admin
- frontend exploration interface (in progress)

The system is functional and supports real exploration workflows, but remains intentionally limited in scope.

### Out of scope (beta)

The following capabilities are planned but not yet fully implemented:

- full frontend exploration interface
- external archive ingestion pipelines
- full-text search
- advanced caching and optimisation strategies
- extended domain modules (materials, movements, etc.)

---

## 2. Design goals

### Primary goals

- Enable relational exploration workflows through structured domain modelling
- Preserve domain integrity by modelling fashion entities explicitly
- Maintain architectural extensibility for future domain expansion
- Allow frontend and backend to evolve independently through a stable API contract

### Quality attributes

- Maintainability through modular architecture
- Performance headroom for large-scale archival datasets
- Clear developer experience and documentation structure

---

## 3. System context

MEMORA consists of three primary components:

- A frontend application built with Next.js
- A backend API implemented using Django REST Framework
- A relational database (SQLite in development, PostgeSQL-ready)

Users interact with the frontend, which communicates with the backend API. The backend manages domain logic, persistence, and editorial workflows.

Django Admin provides a dedicated editorial interface for managing archival data.

---

## 4. High-level architecture

The system follows a standard API-first web architecture:

                        User Browser

                             ↓

                      Next.js Frontend

                             ↓

                      Django REST API

                             ↓

                    Relational Database

The frontend handles user interaction and exploration.

The backend manages domain logic, validation, persistence, and editorial control.

The database stores relational domain entities.

---

## 5. Backend architecture

The backend is organised into modular Django application:

apps/
pieces/
designers/
common/

Each module encapsulates a specific domain entity and its associated logic.

This modular structure preserves domain clarity and enables independent evolution of domain modules.

### Domain model

The domain model consists of explicit relational entities:

- Piece: central archival entity
- Designer: creator entity
- Era: historical context
- Category: typological classification
- Maison: institutional context

Relationships between these entities form the primary navigational structure of the system.

### API layer

The backend exposes the domain model through a REST API implemented using Django REST Framework.

Core responsibilities include:

- exposing domain entities as structured resources
- validating and serializing domain data
- enforcing access control
- supporting relational exploration through filtering

Filtering is implemented as a core exploration capability and supports relational and attribute-base queries.

### Editorial control

Editorial controm is managed through:

- Django Admin interface
- publication flags (`is_published`, `featured`)
- API permission classes

This ensures clear separation between editorial management and public exploration.

---

## 6. Frontend architecture

The frontend is implemented using Next.js and provides the user exploration interface.

### Responsibilities

The frontend is responsible for:

- presenting relational archival data
- enabling navigation across domain relationships
- managing user interaction and exploration flows

### Data fetching strategy

The frontend communicates with the backend through a centralized API client.

Data fetching uses a structured query client to manage:

- server state synchronization
- caching
- loading and error handling

This architecture ensures consistent and scalable data access patterns.

### Theme system

The frontend includes a structured theme system based on tokens and a theme registry.

This enables visual consistency and future evolution of the interface without affecting application logic.

---

## 7. Performance and scalability approach

The architecture is designed to scale as archival data grows.

Key principles include:

- relational database optimization through indexing
- efficient ORM query patterns
- API-based architecture enabling horizontal scaling

Future optimisations will include caching, search optmisation, and database tuning.

---

## 8. Security and reliability

### Access model

The system enforces a read-public, write-restricted access model.

Read access is public.

Write access is restricted to administrative users through Django Admin and API permissions.

### Reliability approach

The system relies on:

- Django's validated request handling
- explicit permission enforcement
- realtional integrity at the database level

---

## 9. Configuration and environments

The backend uses environment-specific Django settings:

- base settings
- development settings
- production-ready configuration

Sensitive values are managed through environment variables.

The system currently uses SQLite in development and is PostgreSQL-ready.

---

## 10. Key decisions and trade-offs

### 10.1 API-first architecture

**Decision:** Use Django REST Framework to expose the domain model through a REST API.

**Why:** Enables independent frontend evolution and establishes a stable system contract.

**Trade-offs:** Requires maintaining separate backend and frontend layers.

**Implications:** API documentation, versioning, and stability are critical.

---

### 10.2 Split frontend and backend

**Decision:** Separate frontend and backend systems.

**Why:** Allows each layer to evolve independently and optmally serve its responsibilities.

**Trade-offs:** Increased architectural complexity.

**Implications:** Requires stable API contracts and clear documentation.

---

### 10.3 Domain-first modelling

**Decision:** Model explicit domain entities and relationships.

**Why:** Aligns system architecture with the relational nature of archival knowledge.

**Trade-offs:** Requires careful relational query optimisation.

**Implications:** Enabes relational exploration workflows.

---

### 10.4 Filtering as a core capability

**Decision:** Implement relational filtering as a primary exploration mechanism.

**Why:** Exploration depends on relational navigation across entities.

**Trade-offs:** Increased query complexity.

**Implications:** Requires careful database optimisations.

---

### 10.5 Editorial control via Django Admin

**Decision:** Use Django Admin and publication flags for editorial management.

**Why:** Enables rapid editorial workflows during beta.

**Trade-offs:** Limited editorial workflow complexity.

**Implications:** Editorial workflows can evolve without architectural changes.

---

### 10.6 Completeness as a quality signal

**Decision:** Treat completeness as a filterable quality signal rather than strict validation.

**Why:** Archival records evolve incrementally.

**Trade-offs:** Completeness definitions may evolve.

**Implications:** Enables progressive enrichment and quality-based exploration.

---

## 11. Known limitations

The current beta has known limitations:

- limited dataset
- incomplete frontend exploration interface
- limited domain modules

These limitations are expected and aligned with beta scope.

---

## 12. Roadmap

Near-term priorities include:

- completing frontend exploration interface
- expanding domain coverage
- improving documentation coverage

---

## 13. Documentation mapping (Diátaxis)

MEMORA documentation follows the Diátaxis framework:

- Tutorials: onboarding and setup
- How-to guides: operational workflows
- Explanation: architecture and design rationale
- Reference: API and domain specifications

