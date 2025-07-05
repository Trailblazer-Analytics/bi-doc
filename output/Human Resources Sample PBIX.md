# Documentation for Human Resources Sample PBIX.pbix

Generated on 2025-07-05 12:28:43

## Overview

**File Type:** Power BI
**File Path:** `C:\SecretProjects\bi-doc\samples\power_bi\Human Resources Sample PBIX.pbix`

## Data Sources

### TableName

- **Type:** Other
- **Connection:** 0                  BU
1                  FP
2             PayType
3    SeparationReason
4                Date
5            Employee
6           Ethnicity
7              Gender
8            AgeGroup
Na...

### Expression

- **Type:** SQL Server
- **Connection:** 0    let\n    Source = Sql.Database(".", "IP", [Que...
1    let\n    Source = Sql.Database(".", "IP", [Que...
2    let\n    Source = Sql.Database(".", "IP", [Que...
3    let\n    Source = Sql.Database...

## Tables and Fields

### AgeGroup

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `AgeGroupID` | Int64 |  |
| `AgeGroup` | string |  |

### BU

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `BU` | string |  |
| `RegionSeq` | string |  |
| `VP` | string |  |
| `Region` | object |  |

### Date

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Date` | datetime64[ns] |  |
| `Month` | string |  |
| `MonthNumber` | Int64 |  |
| `Period` | string |  |
| `PeriodNumber` | Int64 |  |
| `Qtr` | Int64 |  |
| `QtrNumber` | string |  |
| `Year` | Int64 |  |
| `Day` | Int64 |  |
| `MonthStartDate` | datetime64[ns] |  |
| `MonthEndDate` | datetime64[ns] |  |
| `MonthIncrementNumber` | object |  |

### DateTableTemplate_92fd358c-bb4c-4d52-9f5b-e9a59dc2315d

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### Employee

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `date` | datetime64[ns] |  |
| `EmplID` | Int64 |  |
| `Gender` | string |  |
| `Age` | Int64 |  |
| `EthnicGroup` | string |  |
| `FP` | string |  |
| `TermDate` | datetime64[ns] |  |
| `isNewHire` | object |  |
| `BU` | string |  |
| `HireDate` | datetime64[ns] |  |
| `PayTypeID` | string |  |
| `TermReason` | string |  |
| `AgeGroupID` | object |  |
| `TenureDays` | Float64 |  |
| `TenureMonths` | object |  |
| `BadHires` | Float64 |  |

### Ethnicity

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Ethnic Group` | string |  |
| `Ethnicity` | string |  |

### FP

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `FP` | string |  |
| `FPDesc` | string |  |

### Gender

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `ID` | string |  |
| `Gender` | string |  |
| `Sort` | Int64 |  |

### LocalDateTable_6f19fed3-1fc0-4f7a-878d-34aca93d6782

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### LocalDateTable_c04ce649-6e25-466f-9bbc-faabfec0fe29

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### LocalDateTable_c9dde99e-7ac1-4e8e-a5f2-c5ffc41d9cac

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### LocalDateTable_cc28ef26-f63a-4bc3-b357-93ab34cd6d9b

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### LocalDateTable_d2ea5b26-668d-4c17-b228-695669b066a6

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### PayType

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `PayTypeID` | string |  |
| `PayType` | string |  |

### SeparationReason

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `SeparationTypeID` | string |  |
| `SeparationReason` | string |  |

## Measures

### EmpCount

**Table:** Employee

**Expression:**

```dax
CALCULATE(COUNT([EmplID]),
    FILTER(ALL('Date'[PeriodNumber]),
    'Date'[PeriodNumber] = MAX('Date'[PeriodNumber])))
```

**Description:** None
**Display Folder:** None

---

### Seps

**Table:** Employee

**Expression:**

```dax
CALCULATE(COUNT([EmplID]), FILTER(Employee, NOT(ISBLANK(Employee[TermDate]))))
```

**Description:** None
**Display Folder:** None

---

### Actives

**Table:** Employee

**Expression:**

```dax
CALCULATE([EmpCount], FILTER(Employee, ISBLANK(Employee[TermDate])))
```

**Description:** None
**Display Folder:** None

---

### New Hires

**Table:** Employee

**Expression:**

```dax
SUM([isNewHire])
```

**Description:** None
**Display Folder:** None

---

### AVG Tenure Days

**Table:** Employee

**Expression:**

```dax
AVERAGE([TenureDays])
```

**Description:** None
**Display Folder:** None

---

### AVG Tenure Months

**Table:** Employee

**Expression:**

```dax
ROUND([AVG Tenure Days]/30, 1)-1
```

**Description:** None
**Display Folder:** None

---

### AVG Age

**Table:** Employee

**Expression:**

```dax
ROUND(AVERAGE([Age]), 0)
```

**Description:** None
**Display Folder:** None

---

### Sum of BadHires

**Table:** Employee

**Expression:**

```dax
SUM([BadHires])
```

**Description:** None
**Display Folder:** None

---

### New Hires SPLY

**Table:** Employee

**Expression:**

```dax
CALCULATE([New Hires], SAMEPERIODLASTYEAR('Date'[Date]))
```

**Description:** None
**Display Folder:** None

---

### Actives SPLY

**Table:** Employee

**Expression:**

```dax
CALCULATE([Actives], SAMEPERIODLASTYEAR('Date'[Date]))
```

**Description:** None
**Display Folder:** None

---

### Seps SPLY

**Table:** Employee

**Expression:**

```dax
CALCULATE([Seps], SAMEPERIODLASTYEAR('Date'[Date]))
```

**Description:** None
**Display Folder:** None

---

### EmpCount SPLY

**Table:** Employee

**Expression:**

```dax
CALCULATE(COUNT([EmplID]),
    FILTER(ALL('Date'[PeriodNumber]),
    'Date'[PeriodNumber] = MAX('Date'[PeriodNumber])),
    SAMEPERIODLASTYEAR('Date'[Date]))
```

**Description:** None
**Display Folder:** None

---

### Seps YoY Var

**Table:** Employee

**Expression:**

```dax
[Seps]-[Seps SPLY]
```

**Description:** None
**Display Folder:** None

---

### Actives YoY Var

**Table:** Employee

**Expression:**

```dax
[Actives]-[Actives SPLY]
```

**Description:** None
**Display Folder:** None

---

### New Hires YoY Var

**Table:** Employee

**Expression:**

```dax
[New Hires]-[New Hires SPLY]
```

**Description:** None
**Display Folder:** None

---

### Seps YoY % Change

**Table:** Employee

**Expression:**

```dax
DIVIDE([Seps YoY VAR], [Seps SPLY])
```

**Description:** None
**Display Folder:** None

---

### Actives YoY % Change

**Table:** Employee

**Expression:**

```dax
DIVIDE([Actives YoY VAR], [Actives SPLY])
```

**Description:** None
**Display Folder:** None

---

### New Hires YoY % Change

**Table:** Employee

**Expression:**

```dax
DIVIDE([New Hires YoY VAR], [New Hires SPLY])
```

**Description:** None
**Display Folder:** None

---

### Bad Hires SPLY

**Table:** Employee

**Expression:**

```dax
CALCULATE([Sum of BadHires], SAMEPERIODLASTYEAR('Date'[Date]))
```

**Description:** None
**Display Folder:** None

---

### Bad Hires YoY Var

**Table:** Employee

**Expression:**

```dax
[Sum of BadHires]-[Bad Hires SPLY]
```

**Description:** None
**Display Folder:** None

---

### Bad Hires YoY % Change

**Table:** Employee

**Expression:**

```dax
DIVIDE([Bad Hires YoY VAR], [Bad Hires SPLY])
```

**Description:** None
**Display Folder:** None

---

### TO %

**Table:** Employee

**Expression:**

```dax
DIVIDE([Seps], [Actives])
```

**Description:** None
**Display Folder:** None

---

### TO % Norm

**Table:** Employee

**Expression:**

```dax
CALCULATE([TO %], ALL(Gender[Gender]), ALL(Ethnicity[Ethnicity]))
```

**Description:** None
**Display Folder:** None

---

### TO % Var

**Table:** Employee

**Expression:**

```dax
[TO %]-[TO % Norm]
```

**Description:** None
**Display Folder:** None

---

### Sep%ofActive

**Table:** Employee

**Expression:**

```dax
DIVIDE([Seps], [Actives])
```

**Description:** None
**Display Folder:** None

---

### Sep%ofSMLYActives

**Table:** Employee

**Expression:**

```dax
DIVIDE([Seps SPLY], [Actives SPLY])
```

**Description:** None
**Display Folder:** None

---

### BadHire%ofActives

**Table:** Employee

**Expression:**

```dax
DIVIDE([Sum of BadHires], [Actives])
```

**Description:** None
**Display Folder:** None

---

### BadHire%ofActiveSPLY

**Table:** Employee

**Expression:**

```dax
DIVIDE([Bad Hires SPLY], [Actives SPLY])
```

**Description:** None
**Display Folder:** None

---

### Count of BU

**Table:** BU

**Expression:**

```dax
COUNTA('BU'[BU])
```

**Description:** None
**Display Folder:** None

---

### Count of Date

**Table:** Date

**Expression:**

```dax
COUNTA('Date'[Date])
```

**Description:** None
**Display Folder:** None

---

## Calculated Columns

### Region

**Table:** BU
**Data Type:** not available

**Expression:**

```dax
MID([RegionSeq], 3, 15)
```

**Description:** not available

---

### MonthIncrementNumber

**Table:** Date
**Data Type:** not available

**Expression:**

```dax
([Year]-MIN([Year]))*12 +[MonthNumber]
```

**Description:** not available

---

### isNewHire

**Table:** Employee
**Data Type:** not available

**Expression:**

```dax
IF(YEAR([date])= YEAR([HireDate])&& MONTH([date])=MONTH([HireDate]), 1)
```

**Description:** not available

---

### AgeGroupID

**Table:** Employee
**Data Type:** not available

**Expression:**

```dax
IF([Age]<30, 1, IF([Age]<50, 2, 3))
```

**Description:** not available

---

### TenureDays

**Table:** Employee
**Data Type:** not available

**Expression:**

```dax
IF([date]-[HireDate]<0, [HireDate]-[date], [date]-[HireDate])
```

**Description:** not available

---

### TenureMonths

**Table:** Employee
**Data Type:** not available

**Expression:**

```dax
CEILING([TenureDays]/30, 1)-1
```

**Description:** not available

---

### BadHires

**Table:** Employee
**Data Type:** not available

**Expression:**

```dax
IF(OR((([HireDate]-[TermDate])*-1) >= 61, ISBLANK([TermDate])), 0, 1)
```

**Description:** not available

---

### Year

**Table:** DateTableTemplate_92fd358c-bb4c-4d52-9f5b-e9a59dc2315d
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo

**Table:** DateTableTemplate_92fd358c-bb4c-4d52-9f5b-e9a59dc2315d
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month

**Table:** DateTableTemplate_92fd358c-bb4c-4d52-9f5b-e9a59dc2315d
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo

**Table:** DateTableTemplate_92fd358c-bb4c-4d52-9f5b-e9a59dc2315d
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter

**Table:** DateTableTemplate_92fd358c-bb4c-4d52-9f5b-e9a59dc2315d
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day

**Table:** DateTableTemplate_92fd358c-bb4c-4d52-9f5b-e9a59dc2315d
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

### Year (2)

**Table:** LocalDateTable_6f19fed3-1fc0-4f7a-878d-34aca93d6782
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo (2)

**Table:** LocalDateTable_6f19fed3-1fc0-4f7a-878d-34aca93d6782
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month (2)

**Table:** LocalDateTable_6f19fed3-1fc0-4f7a-878d-34aca93d6782
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo (2)

**Table:** LocalDateTable_6f19fed3-1fc0-4f7a-878d-34aca93d6782
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter (2)

**Table:** LocalDateTable_6f19fed3-1fc0-4f7a-878d-34aca93d6782
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day (2)

**Table:** LocalDateTable_6f19fed3-1fc0-4f7a-878d-34aca93d6782
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

### Year (3)

**Table:** LocalDateTable_d2ea5b26-668d-4c17-b228-695669b066a6
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo (3)

**Table:** LocalDateTable_d2ea5b26-668d-4c17-b228-695669b066a6
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month (3)

**Table:** LocalDateTable_d2ea5b26-668d-4c17-b228-695669b066a6
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo (3)

**Table:** LocalDateTable_d2ea5b26-668d-4c17-b228-695669b066a6
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter (3)

**Table:** LocalDateTable_d2ea5b26-668d-4c17-b228-695669b066a6
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day (3)

**Table:** LocalDateTable_d2ea5b26-668d-4c17-b228-695669b066a6
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

### Year (4)

**Table:** LocalDateTable_c9dde99e-7ac1-4e8e-a5f2-c5ffc41d9cac
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo (4)

**Table:** LocalDateTable_c9dde99e-7ac1-4e8e-a5f2-c5ffc41d9cac
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month (4)

**Table:** LocalDateTable_c9dde99e-7ac1-4e8e-a5f2-c5ffc41d9cac
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo (4)

**Table:** LocalDateTable_c9dde99e-7ac1-4e8e-a5f2-c5ffc41d9cac
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter (4)

**Table:** LocalDateTable_c9dde99e-7ac1-4e8e-a5f2-c5ffc41d9cac
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day (4)

**Table:** LocalDateTable_c9dde99e-7ac1-4e8e-a5f2-c5ffc41d9cac
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

### Year (5)

**Table:** LocalDateTable_cc28ef26-f63a-4bc3-b357-93ab34cd6d9b
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo (5)

**Table:** LocalDateTable_cc28ef26-f63a-4bc3-b357-93ab34cd6d9b
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month (5)

**Table:** LocalDateTable_cc28ef26-f63a-4bc3-b357-93ab34cd6d9b
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo (5)

**Table:** LocalDateTable_cc28ef26-f63a-4bc3-b357-93ab34cd6d9b
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter (5)

**Table:** LocalDateTable_cc28ef26-f63a-4bc3-b357-93ab34cd6d9b
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day (5)

**Table:** LocalDateTable_cc28ef26-f63a-4bc3-b357-93ab34cd6d9b
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

### Year (6)

**Table:** LocalDateTable_c04ce649-6e25-466f-9bbc-faabfec0fe29
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo (6)

**Table:** LocalDateTable_c04ce649-6e25-466f-9bbc-faabfec0fe29
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month (6)

**Table:** LocalDateTable_c04ce649-6e25-466f-9bbc-faabfec0fe29
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo (6)

**Table:** LocalDateTable_c04ce649-6e25-466f-9bbc-faabfec0fe29
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter (6)

**Table:** LocalDateTable_c04ce649-6e25-466f-9bbc-faabfec0fe29
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day (6)

**Table:** LocalDateTable_c04ce649-6e25-466f-9bbc-faabfec0fe29
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

## Relationships

- **Employee**[`date`] → **Date**[`Date`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`FP`] → **FP**[`FP`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`EthnicGroup`] → **Ethnicity**[`Ethnic Group`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`Gender`] → **Gender**[`ID`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`PayTypeID`] → **PayType**[`PayTypeID`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`BU`] → **BU**[`BU`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`AgeGroupID`] → **AgeGroup**[`AgeGroupID`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`TermReason`] → **SeparationReason**[`SeparationTypeID`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Date**[`Date`] → **None**[`None`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Date**[`MonthStartDate`] → **None**[`None`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Date**[`MonthEndDate`] → **None**[`None`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`TermDate`] → **None**[`None`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **Employee**[`HireDate`] → **None**[`None`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

## Report Structure

### Page: Info

### Page: New Hires

### Page: Actives and Separations

### Page: Bad Hires

### Page: New Hires Scorecard

## Power Query (M Code)

### queries

```m
[]
```

### data_sources

```m
[]
```

### parameters

```m
[]
```

### TableName (2)

```m
{0: 'BU', 1: 'FP', 2: 'PayType', 3: 'SeparationReason', 4: 'Date', 5: 'Employee', 6: 'Ethnicity', 7: 'Gender', 8: 'AgeGroup'}
```

### Expression (2)

```m
{0: 'let\n    Source = Sql.Database(".", "IP", [Query="select distinct market BU,#(lf)  REGIONTITLE Region,#(lf)  MARKETDIRECTOR VP#(lf)from hr.bu"]),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"BU", "BU"}, {"Region", "RegionSeq"}, {"VP", "VP"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"BU", type text}, {"RegionSeq", type text}, {"VP", type text}})\nin\n    #"Changed Type"', 1: 'let\n    Source = Sql.Database(".", "IP", [Query="SELECT [HR].[FP].*   FROM [HR].[FP]"]),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"FP", "FP"}, {"FPDesc", "FPDesc"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"FP", type text}, {"FPDesc", type text}})\nin\n    #"Changed Type"', 2: 'let\n    Source = Sql.Database(".", "IP", [Query="select distinct PayTypeID, [Hrly-Salaried] PayType#(lf)from [HR].[PayGroup]"]),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"PayTypeID", "PayTypeID"}, {"PayType", "PayType"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"PayTypeID", type text}, {"PayType", type text}})\nin\n    #"Changed Type"', 3: 'let\n    Source = Sql.Database(".", "IP", [Query="SELECT distinct SeparationTypeID, [Vol-Invol] SeparationReason#(lf)  FROM [IP].[HR].[TermReason]"]),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"SeparationTypeID", "SeparationTypeID"}, {"SeparationReason", "SeparationReason"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"SeparationTypeID", type text}, {"SeparationReason", type text}})\nin\n    #"Changed Type"', 4: 'let\n    Source = Sql.Database(".", "IP", [Query="SELECT [HR].[Date].*   FROM [HR].[Date]"]),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"Date", "Date"}, {"Month", "Month"}, {"MonthNumber", "MonthNumber"}, {"Period", "Period"}, {"PeriodNumber", "PeriodNumber"}, {"Qtr", "Qtr"}, {"QtrNumber", "QtrNumber"}, {"Year", "Year"}, {"Day", "Day"}, {"MonthStartDate", "MonthStartDate"}, {"MonthEndDate", "MonthEndDate"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"Date", type datetime}, {"Month", type text}, {"MonthNumber", Int64.Type}, {"Period", type text}, {"PeriodNumber", Int64.Type}, {"Qtr", Int64.Type}, {"QtrNumber", type text}, {"Year", Int64.Type}, {"Day", Int64.Type}, {"MonthStartDate", type datetime}, {"MonthEndDate", type datetime}})\nin\n    #"Changed Type"', 5: 'let\n    Source = Sql.Database(".", "IP", [Query="SELECT dateadd(year, 1, d.date) Date#(lf)  ,Market BU#(lf)  ,[EmplID]#(lf)  ,iif([Gender]=\'M\', \'C\', \'D\') Gender --  ,iif([Gender]=\'M\', \'F\', \'M\') Gender#(lf)  ,[Age] - (2013 - year(d.date)) Age#(lf)  ,[EthnicGroup]#(lf)  ,[FP]#(lf)  ,dateadd(year, 1, [SenDate]) HireDate#(lf)  ,p.PayTypeID#(lf)  ,null [TermDate]#(lf)  ,null [TermReason]#(lf) FROM [IP].[HR].[AllEmps] E , [HR].[Date] d , [HR].[BU] b , hr.PayGroup p --, hr.TermReason t#(lf) where d.day = 1 and e.SenDate <= d.MonthEndDate and isnull(e.termdate, \'9999-01-01\') >= d.MonthEndDate and d.Date < \'2014-01-01\'#(lf)  and p.PayGroup = e.PayGroup#(lf)  and b.UNIT = e.Unit and [EmplID] % 2 = 0#(lf)union all#(lf)--seps#(lf)SELECT dateadd(year, 1, d.date) Date#(lf)    ,Market BU#(lf)      ,[EmplID]#(lf)      ,iif([Gender]=\'M\', \'C\', \'D\') Gender#(lf)      ,[Age] - (2013 - year(d.date)) Age#(lf)      ,[EthnicGroup]#(lf)      ,[FP]#(lf)      ,dateadd(year, 1,[SenDate]) HireDate#(lf)      ,p.PayTypeID#(lf)      ,dateadd(year, 1, [TermDate]) [TermDate]#(lf)      ,t.[SeparationTypeID] [TermReason]#(lf)  FROM [IP].[HR].[AllEmps] E, [HR].[Date] d , [HR].[BU] b, hr.PayGroup p , hr.TermReason t#(lf) where d.day = 1 and e.TermDate <= d.MonthEndDate and e.TermDate >= d.MonthStartDate and d.Date < \'2014-01-01\'#(lf)  and p.PayGroup = e.PayGroup #(lf)  and t.[Term-Discharge]= e.[Term-Discharge]#(lf)  and b.UNIT = e.Unit and [EmplID] % 2 = 0"]),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"date", "date"}, {"EmplID", "EmplID"}, {"Gender", "Gender"}, {"Age", "Age"}, {"EthnicGroup", "EthnicGroup"}, {"FP", "FP"}, {"TermDate", "TermDate"}, {"BU", "BU"}, {"HireDate", "HireDate"}, {"PayTypeID", "PayTypeID"}, {"TermReason", "TermReason"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"date", type datetime}, {"EmplID", Int64.Type}, {"Gender", type text}, {"Age", Int64.Type}, {"EthnicGroup", type text}, {"FP", type text}, {"TermDate", type datetime}, {"BU", type text}, {"HireDate", type datetime}, {"PayTypeID", type text}, {"TermReason", type text}})\nin\n    #"Changed Type"', 6: 'let\n    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WMlTSUXIvyi8tUHBUitWJVjKC853AfGM43xnMN4HzXcB8UzjfFcw3g/PdwHxzON9dKTYWAA==", BinaryEncoding.Base64), Compression.Deflate))),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"Column1", "Ethnic Group"}, {"Column2", "Ethnicity"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"Ethnic Group", type text}, {"Ethnicity", type text}})\n in\n    #"Changed Type"', 7: 'let\n    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WclHSUfJNzEkFUoZKsTrRSs5AlltqLkTISCk2FgA=", BinaryEncoding.Base64), Compression.Deflate))),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"Column1", "ID"}, {"Column2", "Gender"}, {"Column3", "Sort"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"ID", type text}, {"Gender", type text}, {"Sort", Int64.Type}})\n in\n    #"Changed Type"', 8: 'let\n    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WMlTSUYopNTAwTjY2UIrViVYyAgoYG+iaWIJ5xkCeqYG2UmwsAA==", BinaryEncoding.Base64), Compression.Deflate))),\n    #"Renamed Columns" = Table.RenameColumns(Source, {{"Column1", "AgeGroupID"}, {"Column2", "AgeGroup"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns", {{"AgeGroupID", Int64.Type}, {"AgeGroup", type text}})\n in\n    #"Changed Type"'}
```

---
Documentation generated by BI Documentation Tool
