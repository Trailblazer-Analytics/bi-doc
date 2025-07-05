# Documentation for COVID-19 US Tracking Sample.pbix

Generated on 2025-07-05 16:30:19

## Overview

**File Type:** Power BI
**File Path:** `C:\SecretProjects\bi-doc\samples\power_bi\COVID-19 US Tracking Sample.pbix`

## Data Sources

### TableName

- **Type:** Other
- **Connection:** 0             COVID
1          StateDim
2             Table
3    COVID measures
Name: TableName, dtype: object

### Expression

- **Type:** Other
- **Connection:** 0    let\n    Source = Table.NestedJoin(Cases, {"Co...
1    let\n    Source = Table.FromRows(Json.Document...
2    let\n    Source = Table.FromRows(Json.Document...
3    let\n    Source = Table.FromRo...

## Tables and Fields

### COVID

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `County Name` | string |  |
| `State` | string |  |
| `Date` | datetime64[ns] |  |
| `Cases` | Int64 |  |
| `FIPS` | string |  |
| `Deaths` | Int64 |  |
| `County` | object |  |
| `Daily cases` | object |  |
| `Daily deaths` | object |  |
| `StateFIPS` | string |  |

### DateTableTemplate_fe7eb183-f12b-4c88-bb89-cfaa7f88e1df

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### LocalDateTable_a0f5b894-4f57-4a54-a9d5-5508aa5843d0

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Year` | object |  |
| `MonthNo` | object |  |
| `Month` | object |  |
| `QuarterNo` | object |  |
| `Quarter` | object |  |
| `Day` | object |  |

### StateDim

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `State` | string |  |
| `State code` | string |  |
| `US territories` | string |  |
| `Country` | object |  |

### Table

| Field Name | Data Type | Description |
|------------|-----------|-------------|
| `Metric` | string |  |
| `Order` | Int64 |  |

## Measures

### Updated

**Table:** COVID

**Expression:**

```dax
"Data provided by USAFacts. Because of the frequency of data upates,
    they may NOT reflect the exact numbers reported by government organizations\nOR the news media. For more information\nOR to download the data,
    please click the logo below. Data updated through " & FORMAT([Max date], "mmmm dd, yyyy")& "."
```

**Description:** None
**Display Folder:** None

---

### Max date

**Table:** COVID

**Expression:**

```dax
CALCULATE(MAX('COVID'[Date]), ALL('COVID'))
```

**Description:** None
**Display Folder:** None

---

### Drill-through button text

**Table:** StateDim

**Expression:**

```dax
IF(SELECTEDVALUE(StateDim[State], 0)==0,
    "Click on a State to view by County ",
    "Click here to view by County IN " & VALUES(StateDim[State code])&" ")
```

**Description:** None
**Display Folder:** None

---

### Methodology

**Table:** Table

**Expression:**

```dax
"This interactive feature aggregates data from the Centers for Disease Control\nAND Prevention(CDC), state-\nAND local-level public health agencies. County-level data is confirmed by referencing state\nAND local agencies directly. Source: USAFacts"
```

**Description:** None
**Display Folder:** None

---

### Notes

**Table:** Table

**Expression:**

```dax
"New York* covers 5 counties(Bronx, Kings, New York, Queens, Richmond), NOT New York county. City of St. Louis was renamed to St. Louis City. City\nAND Borough of Juneau was renamed to Juneau Borough. Municipality of Anchorage was renamed to Anchorage. Jackson County includes other portions of Kansas City. Source: USAFacts"
```

**Description:** None
**Display Folder:** None

---

### Total confirmed cases

**Table:** COVID measures

**Expression:**

```dax
SUM('COVID'[Daily cases])
```

**Description:** None
**Display Folder:** None

---

### Total deaths

**Table:** COVID measures

**Expression:**

```dax
SUM(COVID[Daily deaths])
```

**Description:** None
**Display Folder:** None

---

### Case fatality rate

**Table:** COVID measures

**Expression:**

```dax
DIVIDE([Total deaths], [Total confirmed cases])
```

**Description:** None
**Display Folder:** None

---

### Confirmed cases

**Table:** COVID measures

**Expression:**

```dax
SUM('COVID'[Cases])
```

**Description:** None
**Display Folder:** None

---

### Deaths

**Table:** COVID measures

**Expression:**

```dax
SUM('COVID'[Deaths])
```

**Description:** None
**Display Folder:** None

---

### Terms of use

**Table:** Table

**Expression:**

```dax
"This report\nAND data are provided " & """" & "as is" & """" & ", " & """" & "with all faults" & """" & ",\nAND without warranty of any kind. Microsoft gives no express warranties\nOR guarantees\nAND expressly disclaims all implied warranties, including merchantability, fitness for a particular purpose,\nAND non-infringement."
```

**Description:** None
**Display Folder:** None

---

## Calculated Columns

### Year

**Table:** DateTableTemplate_fe7eb183-f12b-4c88-bb89-cfaa7f88e1df
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo

**Table:** DateTableTemplate_fe7eb183-f12b-4c88-bb89-cfaa7f88e1df
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month

**Table:** DateTableTemplate_fe7eb183-f12b-4c88-bb89-cfaa7f88e1df
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo

**Table:** DateTableTemplate_fe7eb183-f12b-4c88-bb89-cfaa7f88e1df
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter

**Table:** DateTableTemplate_fe7eb183-f12b-4c88-bb89-cfaa7f88e1df
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day

**Table:** DateTableTemplate_fe7eb183-f12b-4c88-bb89-cfaa7f88e1df
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

### County

**Table:** COVID
**Data Type:** not available

**Expression:**

```dax
'COVID'[County Name] & ", " & 'COVID'[State]
```

**Description:** not available

---

### Daily cases

**Table:** COVID
**Data Type:** not available

**Expression:**

```dax
VAR __CountyName = 'COVID'[County Name]\nVAR __State = 'COVID'[State]\nVAR __Yesterday = DATEADD(COVID[Date], -1, DAY)\nVAR __TodaysCases = 'COVID'[Cases]\nRETURN __TodaysCases - CALCULATE(SUM('COVID'[Cases]),
    FILTER(COVID, COVID[Date] = __Yesterday && COVID[County Name] = __CountyName && COVID[State] = __State))+ 0
```

**Description:** not available

---

### Daily deaths

**Table:** COVID
**Data Type:** not available

**Expression:**

```dax
VAR __CountyName = 'COVID'[County Name]\nVAR __State = 'COVID'[State]\nVAR __Yesterday = DATEADD(COVID[Date], -1, DAY)\nVAR __TodaysDeaths = 'COVID'[Deaths]\nRETURN __TodaysDeaths - CALCULATE(SUM('COVID'[Deaths]),
    FILTER(COVID, COVID[Date] = __Yesterday && COVID[County Name] = __CountyName && COVID[State] = __State))+ 0
```

**Description:** not available

---

### Country

**Table:** StateDim
**Data Type:** not available

**Expression:**

```dax
"USA"
```

**Description:** not available

---

### Year (2)

**Table:** LocalDateTable_a0f5b894-4f57-4a54-a9d5-5508aa5843d0
**Data Type:** not available

**Expression:**

```dax
YEAR([Date])
```

**Description:** not available

---

### MonthNo (2)

**Table:** LocalDateTable_a0f5b894-4f57-4a54-a9d5-5508aa5843d0
**Data Type:** not available

**Expression:**

```dax
MONTH([Date])
```

**Description:** not available

---

### Month (2)

**Table:** LocalDateTable_a0f5b894-4f57-4a54-a9d5-5508aa5843d0
**Data Type:** not available

**Expression:**

```dax
FORMAT([Date], "MMMM")
```

**Description:** not available

---

### QuarterNo (2)

**Table:** LocalDateTable_a0f5b894-4f57-4a54-a9d5-5508aa5843d0
**Data Type:** not available

**Expression:**

```dax
INT(([MonthNo] + 2)/ 3)
```

**Description:** not available

---

### Quarter (2)

**Table:** LocalDateTable_a0f5b894-4f57-4a54-a9d5-5508aa5843d0
**Data Type:** not available

**Expression:**

```dax
"Qtr " & [QuarterNo]
```

**Description:** not available

---

### Day (2)

**Table:** LocalDateTable_a0f5b894-4f57-4a54-a9d5-5508aa5843d0
**Data Type:** not available

**Expression:**

```dax
DAY([Date])
```

**Description:** not available

---

## Relationships

- **COVID**[`Date`] → **None**[`None`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

- **COVID**[`State`] → **StateDim**[`State code`]
  - Cardinality: M:1
  - Active: Yes
  - Cross Filter: Single

## Report Structure

### Page: Main

### Page: County view

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
{0: 'COVID', 1: 'StateDim', 2: 'Table', 3: 'COVID measures'}
```

### Expression (2)

```m
{0: 'let\n    Source = Table.NestedJoin(Cases, {"County Name", "State", "StateFIPS", "Date", "FIPS"}, Deaths, {"County Name", "State", "StateFIPS", "Date", "FIPS"}, "Deaths", JoinKind.LeftOuter),\n    #"Expanded Deaths" = Table.ExpandTableColumn(Source, "Deaths", {"Deaths"}, {"Deaths.1"}),\n    #"Renamed Columns" = Table.RenameColumns(#"Expanded Deaths",{{"Deaths.1", "Deaths"}}),\n    #"Changed Type" = Table.TransformColumnTypes(#"Renamed Columns",{{"Date", type date}}),\n    #"Replaced Value" = Table.ReplaceValue(#"Changed Type","Jackson County (including other portions of Kansas City)","Jackson County",Replacer.ReplaceText,{"County Name"}),\n    #"Replaced Value1" = Table.ReplaceValue(#"Replaced Value","New York City","New York*",Replacer.ReplaceText,{"County Name"}),\n    #"Replaced Value2" = Table.ReplaceValue(#"Replaced Value1","City of St. Louis","St. Louis City",Replacer.ReplaceText,{"County Name"}),\n    #"Replaced Value3" = Table.ReplaceValue(#"Replaced Value2","City and Borough of Juneau","Juneau Borough",Replacer.ReplaceText,{"County Name"}),\n    #"Replaced Value4" = Table.ReplaceValue(#"Replaced Value3","Municipality of Anchorage","Anchorage",Replacer.ReplaceText,{"County Name"}),\n    #"Changed Type1" = Table.TransformColumnTypes(#"Replaced Value4",{{"Cases", Int64.Type}, {"Deaths", Int64.Type}})\nin\n    #"Changed Type1"', 1: 'let\n    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("XZTRbuowDIZfpeJ62jsgykbHmlYU6DjTLkyb0ahtjJJ0jPP0J07ZqZmEkPq5sX/7j/v+Ppt3cIQeZg+z+av/Ezj7eAjUtgGuGTTqL+pA/3DagrZgCW8mvIBOfaLRit5fzFkAOzRQI+GMY61l5VQ1OIpsp0gsO7iAkZ7Eywk/+TSqpuxPTPizRHMKNZ9ZzZVPoJR/XiUTTGpoSEUSM9Z1SqOiZhKWNdG1gtB5IhjFS0Cs0PpnFOuCQandULVXwocJv+Kg7C3tK8uRgtLUbLrkzFw70DXhmGNroWoGK52jqilPo6pGnUATTjj2c7boqGoqOLeWfuczzSkt7iM4mICZYSlqN4pPmVlCHs3t6oglx18QvBJ7Di/RCvqzbVRwV6zuYy/SWElTEy/3gVR+q4qsE+l94ICmJcKmLNC4JlqAQe9sULD4HYyhHech2GizRlGFjGnK2s7fmLArGVuLzMgT0pgzdv1zqbW9dl8wLkDOjNk0WMsosTc/N8ycAod7scXid/C/2IKJ3Uoy1Uqa4lZw/h1u4/ZtYjsHjX/aMdP20vTeTQ/2nCq/SaP8PZNfgvdLn1xoueQBaV3EDpXM6lLZCrVV4QxruLxi75MRZZ7Ne2lUBToqoMfwvaHreJB2XPEBetrvHWPBSGl05BeFVuo23rATOXsvH6RxGG3G65NvWGj3WDze5LPT+4S9EivrvDAX4WfkP2NDfwyNxsykHDoYKHX5c+7jHw==", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type text) meta [Serialized.Text = true]) in type table [State = _t, #"State code" = _t, #"US territories" = _t]),\n    #"Changed Type" = Table.TransformColumnTypes(Source,{{"State", type text}, {"State code", type text}, {"US territories", type text}})\nin\n    #"Changed Type"', 2: 'let\n    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45Wcs7PS8ssyk1NUXBOLE4tVtJRMlSK1YlWcklNLMkAcY3AXJCkgltiSWJOZkmlQlBiSSpQylgpNhYA", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type text) meta [Serialized.Text = true]) in type table [Metric = _t, Order = _t]),\n    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Metric", type text}, {"Order", Int64.Type}})\nin\n    #"Changed Type"', 3: 'let\n    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText("i45WMlSKjQUA", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type text) meta [Serialized.Text = true]) in type table [Column1 = _t]),\n    #"Changed Type" = Table.TransformColumnTypes(Source,{{"Column1", Int64.Type}}),\n    #"Removed Columns" = Table.RemoveColumns(#"Changed Type",{"Column1"})\nin\n    #"Removed Columns"'}
```

---
Documentation generated by BI Documentation Tool
