# Documentation for CH2_BBOD_CourseMetrics_v2.twbx

Generated on 2025-07-05 12:26:16

## Overview

**File Type:** Tableau
**File Path:** `C:\SecretProjects\bi-doc\samples\tableau\CH2_BBOD_CourseMetrics_v2.twbx`

## Data Sources

### federated.1y0ubnb1p8wit416uqf3d1p4fd9m

**Caption:** Students (Course Metrics Dashboard Data)

#### Connections

- **Type:** excel-direct
- **Server:**
- **Database:** None

#### Fields

| Field Name | Caption | Data Type | Role | Type | Calculated |
|------------|---------|-----------|------|------|------------|
| `Semester` | None | string | None | None | No |
| `Year` | None | string | None | None | No |
| `Year-Semester` | None | string | None | None | No |
| `Students` | None | integer | None | None | No |
| `[Number of Records]` | None | integer | measure | quantitative | Yes |
| `[Students]` | None | integer | measure | quantitative | No |
| `[Year-Semester]` | None | string | dimension | nominal | No |
| `Semester` | None | string | None | None | No |
| `Year` | None | string | None | None | No |

### federated.03gehrm1kx3q4s14fmnoz1pg9ldz

**Caption:** Ratings (Course Metrics Dashboard Data)

#### Connections (2)

- **Type:** excel-direct
- **Server:**
- **Database:** None

#### Fields (2)

| Field Name | Caption | Data Type | Role | Type | Calculated |
|------------|---------|-----------|------|------|------------|
| `Semester` | None | string | None | None | No |
| `Year` | None | string | None | None | No |
| `Year-Semester` | None | string | None | None | No |
| `Year-Semester (group)` | None | string | None | None | No |
| `Rating` | None | real | None | None | No |
| `Students` | None | integer | None | None | No |
| `[Number of Records]` | None | integer | measure | quantitative | Yes |
| `[Year-Semester (group)]` | None | string | dimension | nominal | No |
| `Semester` | None | string | None | None | No |
| `Year` | None | string | None | None | No |
| `Year-Semester` | None | string | None | None | No |
| `Rating` | None | real | None | None | No |
| `Students` | None | integer | None | None | No |

### federated.1txd47502bl6lf10f5zkn1lyfx00

**Caption:** Evaluations (Course Metrics Dashboard Data)

#### Connections (3)

- **Type:** excel-direct
- **Server:**
- **Database:** None

#### Fields (3)

| Field Name | Caption | Data Type | Role | Type | Calculated |
|------------|---------|-----------|------|------|------------|
| `Date` | None | date | None | None | No |
| `Entity` | None | string | None | None | No |
| `Questions` | None | string | None | None | No |
| `Semesters` | None | string | None | None | No |
| `Mean Rating` | None | real | None | None | No |
| `[Entity]` | None | string | dimension | nominal | No |
| `[Number of Records]` | None | integer | measure | quantitative | Yes |
| `Date` | None | date | None | None | No |
| `Questions` | None | string | None | None | No |
| `Semesters` | None | string | None | None | No |
| `Mean Rating` | None | real | None | None | No |

### federated.10xvqqd0b5nzde1gej6o01bagq41

**Caption:** Enrollments and Classes (Course Metrics Dashboard Data)

#### Connections (4)

- **Type:** excel-direct
- **Server:**
- **Database:** None

#### Fields (4)

| Field Name | Caption | Data Type | Role | Type | Calculated |
|------------|---------|-----------|------|------|------------|
| `Year` | None | string | None | None | No |
| `#` | None | integer | None | None | No |
| `# Classes` | None | integer | None | None | No |
| `Year2` | Year2 | string | dimension | nominal | Yes |
| `[Number of Records]` | None | integer | measure | quantitative | Yes |
| `[Year (group)]` | None | string | dimension | nominal | No |
| `[Year]` | None | string | dimension | nominal | No |
| `#` | None | integer | None | None | No |
| `# Classes` | None | integer | None | None | No |

## Calculated Fields

### [Number of Records]

**Data Source:** federated.1y0ubnb1p8wit416uqf3d1p4fd9m
**Data Type:** integer
**Role:** measure

**Calculation:**

```sql
1
```

**Description:** not available

---

### [Number of Records] (2)

**Data Source:** federated.03gehrm1kx3q4s14fmnoz1pg9ldz
**Data Type:** integer
**Role:** measure

**Calculation:**

```sql
1
```

**Description:** not available

---

### [Number of Records] (3)

**Data Source:** federated.1txd47502bl6lf10f5zkn1lyfx00
**Data Type:** integer
**Role:** measure

**Calculation:**

```sql
1
```

**Description:** not available

---

### Year2

**Data Source:** federated.10xvqqd0b5nzde1gej6o01bagq41
**Data Type:** string
**Role:** dimension

**Calculation:**

```sql
[Year]
```

**Description:** not available

**Used in Worksheets:** `Enrollments`,`Classes`

---

### [Number of Records] (4)

**Data Source:** federated.10xvqqd0b5nzde1gej6o01bagq41
**Data Type:** integer
**Role:** measure

**Calculation:**

```sql
1
```

**Description:** not available

---

## Worksheets

### Alternate Legend

### Alternate Legend 2

### Classes

### Enrollments

### Evaluation Ranking

### Ratings

### Students

## Dashboards

### Course Metrics Dashboard

**Contains Worksheets:**

### The Big Book of Dashboards

**Contains Worksheets:**

## Field Usage Summary

| Field | Used in Worksheets |
|-------|-------------------|
| `by_worksheet` |  |
| `by_dashboard` |  |
| `unused_fields` |  |
| `most_used_fields` |  |
| `field_dependencies` |  |
| `[Students]`|`Students` |
| `[Year-Semester]`|`Students` |
| `Semester`|`Ratings` |
| `Year`|`Ratings` |
| `[Year-Semester (group)]`|`Ratings` |
| `Year-Semester`|`Ratings` |
| `Rating`|`Ratings` |
| `[Entity]`|`Alternate Legend 2`,`Evaluation Ranking` |
| `Questions`|`Evaluation Ranking` |
| `Semesters`|`Evaluation Ranking` |
| `Mean Rating`|`Evaluation Ranking` |
| `Year2`|`Enrollments`,`Classes` |
| `[Year (group)]`|`Enrollments`,`Classes` |
| `[Year]`|`Enrollments`,`Classes` |
| `#`|`Enrollments` |
| `# Classes`|`Classes` |

---
Documentation generated by BI Documentation Tool
