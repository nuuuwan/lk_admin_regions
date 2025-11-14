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

### Example Regions and Code

| Level    | id pattern         | Example                                             |
| -------- | ------------------ | --------------------------------------------------- |
| Country  | `LK`               | Sri Lanka `LK`                                      |
| Province | `LK-P`             | Western Province `LK-1`                             |
| District | `LK-P-D`           | Colombo District `LK-1-1` or `LK-11`                |
| DSD      | `LK-P-D-DSD`       | Thimbirigasyaya `LK-1-1-27` or `LK-1127`            |
| GND      | `LK-P-D-DSD-GND`   | Kollupitiya `LK-1-1-27-005` or `LK1127005`          |
| Village  | `LK-P-D-DSD-GND-V` | Rotunda Gardens `LK-1-1-27-005-02` or `LK112700502` |

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

