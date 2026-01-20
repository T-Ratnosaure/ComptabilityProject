# Architecture: [Feature Name]

**Date:** [YYYY-MM-DD]
**PRD Reference:** [link to PRD]
**Status:** DRAFT / APPROVED

---

## Overview

[High-level architecture description]

---

## Components

### Component 1: [Name]

**Purpose:** [what it does]

**Location:** `src/[path]/`

**Interfaces:**
- Input: [description]
- Output: [description]

**Dependencies:**
- [dependency 1]
- [dependency 2]

### Component 2: [Name]

[repeat structure]

---

## Data Flow

```
[Source] → [Process 1] → [Process 2] → [Destination]
```

[Description of data flow]

---

## File Changes

| File | Change Type | Description |
|------|-------------|-------------|
| `src/[path]/file.py` | NEW / MODIFY | [description] |
| [file] | [type] | [description] |

---

## Tax Domain Considerations

### Tax Engine Impact
- [ ] Changes to `src/tax_engine/`
- [ ] Changes to `src/analyzers/`
- [ ] No tax engine impact

### Data Sources
- [ ] New barème data needed
- [ ] New rules JSON needed
- [ ] No new data sources

### Verification Requirements
- [ ] Official source required
- [ ] Manual calculation verification
- [ ] Automated tests sufficient

---

## Technical Decisions

| Decision | Options Considered | Chosen | Rationale |
|----------|-------------------|--------|-----------|
| [decision] | A, B, C | A | [why] |
| [decision] | A, B | B | [why] |

---

## Testing Strategy

### Unit Tests
- [ ] [test area 1]
- [ ] [test area 2]

### Integration Tests
- [ ] [test area 1]

### Manual Verification
- [ ] [verification needed]

---

## Security Considerations

- [ ] PII handling changes
- [ ] Authentication changes
- [ ] API security changes
- [ ] No security impact

---

## Rollback Plan

[How to rollback if issues occur]

---

## Approval

- [ ] Architecture reviewed
- [ ] Tax implications assessed
- [ ] Security assessed
- [ ] Ready for implementation
