# Sri Lanka's Administrative Regions 🇱🇰 (lk_admin_regions)

This repository provides structured information on Sri Lanka's administrative regions. It documents the official hierarchy, codes, and region ID formats used across national datasets.

Sri Lanka’s territorial administration follows a fixed hierarchy used in government datasets, censuses, and geospatial systems. 

## Hierarchy

1. **Country**: The sovereign state of Sri Lanka. National laws, taxation, defence, foreign policy and countrywide administration are governed at this level.

2. **Province**: One of nine large administrative regions. Provinces have elected Provincial Councils responsible for education, health, local transport, and certain development functions.

3. **District**: One of 25 subdivisions of provinces. Districts are headed by District Secretaries who coordinate central government functions, disaster management, elections, and regional planning.

4. **Divisional Secretariat Division (DSD)**: Subdistrict administrative units led by Divisional Secretaries. They manage land administration, social welfare programmes, permits, civil registrations, and coordination of village-level activities.

5. **Grama Niladhari Division (GND)**: The smallest government administrative unit with an appointed Grama Niladhari officer. Responsible for population records, household enumeration, certificates, dispute reporting, and acting as the state's representative at the community level.

6. **Village**: The smallest named settlement or locality. Villages do not have formal administrative power but are used in census work, local planning, election mapping, and community-level identification.

## Region ID Structure

This repository uses the ISO 3166-1 alpha-2 codes as the primary key for every region. A region's code comprises its parent region's code followed by a numerical code. These segments reflect the nested administrative hierarchy and ensure consistent ordering.

The ISO 3166-2 standard, which defines codes for the principal subdivisions of countries, was first published in December 1998. This established the framework for standardized region identifiers used in this repository.

### Example Regions and Codes

| Level    | ID Pattern         | Example                                             |
| -------- | ------------------ | --------------------------------------------------- |
| Country  | `LK`               | Sri Lanka `LK`                                      |
| Province | `LK-P`             | Western Province `LK-1`                             |
| District | `LK-P-D`           | Colombo District `LK-1-1` or `LK-11`                |
| DSD      | `LK-P-D-DSD`       | Thimbirigasyaya `LK-1-1-27` or `LK-1127`            |
| GND      | `LK-P-D-DSD-GND`   | Kollupitiya `LK-1-1-27-005` or `LK1127005`          |
| Village  | `LK-P-D-DSD-GND-V` | Rotunda Gardens `LK-1-1-27-005-02` or `LK112700502` |


## How Region IDs Were Assigned

While numbering began after December 1998, the current order of numbering reflects the history of Sri Lanka's administrative divisions. 


### 1833

Following the recommendations of the Colebrooke-Cameron Commission, five provinces under one administration came into being: 

- LK-1: Western Province – The maritime districts of Colombo, Chilaw and Puttalam, and the Kandyan provinces of Three Korales, Four Korales, Seven Korales and Lower Bulathgama.
- LK-2: Central Province – The central Kandyan Provinces.
- LK-3: Southern Province – The maritime districts of Galle, Hambantota, Matara and Tangalle, and the Kandyan provinces of Lower Uva, Saffragam and Wellassa.
- LK-4: Northern Province – The maritime districts of Jaffna, Mannar and Vanni, and the Kandyan province of Nuwara Kalawiya.
- LK-5: Eastern Province – The maritime districts of Batticaloa and Trincomalee, and the Kandyan provinces of Bintenna and Tamankaduwa.

### 1845 to 1889

Since, 4 additional provinces were created by carving out parts of existing provinces.

- LK-6: The North Western Province was created in 1845, from northern parts of the Western Province (the districts of Chilaw, Puttalam and Seven Korales).
- LK-7: The North Central Province was created in 1873 from southern parts of the Northern Province (district of Nuwara Kalawiya) and north western parts of the Eastern Province (district of Tamankaduwa).
- LK-8: The Uva Province was created in 1886 from parts of the Central Province, Eastern Province (district of Bintenna) and Southern Province (district of Wellassa).
- LK-9: The Sabaragamuwa Province was created in 1889, from modern day Ratnapura District, which was part of the Southern Province, and Kegalle, which was part of the Western Province.

## Repository Scope

This repository contains the administrative hierarchy of Sri Lanka and a small set of core attributes for each region, such as population and land area where available.

It does not include geospatial boundary data, shapefiles, coordinates, or maps. 

The focus is on a clean, structured hierarchy and essential non-geometric metadata.

## Sources

- Department of Census and Statistics, Sri Lanka: [https://www.statistics.gov.lk](https://www.statistics.gov.lk)
- Ministry of Public Administration: [https://pubad.gov.lk](https://pubad.gov.lk)
- ISO 3166 Online Browsing Platform (Sri Lanka LK): [https://www.iso.org/obp/ui/#iso:code:3166:LK](https://www.iso.org/obp/ui/#iso:code:3166:LK)
- ISO 3166-2 Standard Overview: [https://www.iso.org/iso-3166-country-codes.html](https://www.iso.org/iso-3166-country-codes.html)
- Wikipedia: ISO 3166-2 LK: [https://en.wikipedia.org/wiki/ISO_3166-2:LK](https://en.wikipedia.org/wiki/ISO_3166-2:LK)
- Wikipedia: Administrative divisions of Sri Lanka: [https://en.wikipedia.org/wiki/Administrative_divisions_of_Sri_Lanka](https://en.wikipedia.org/wiki/Administrative_divisions_of_Sri_Lanka)

