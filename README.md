# Sri Lanka's Administrative Regions 🇱🇰 (lk_admin_regions)

![LastUpdated](https://img.shields.io/badge/last_updated-2025--12--07-green)

This repository provides structured information on Sri Lanka's administrative regions, documenting the official hierarchy, codes, and region ID formats used across national datasets.

Sri Lanka’s territorial administration follows a fixed hierarchy utilized in government datasets, censuses, and geospatial systems.

## Data

- **[Entity Data](data/ents)**: Tabular data containing basic information about administrative regions. Available in **TSV** and **JSON** formats.
- **[Geo Data](data/geo)**: Geographical information about administrative regions. Available in **GeoJSON**, **TopoJSON**, and plain **JSON** formats, with multiple levels of precision. See [data/geo](data/geo/README.md) for details.

## Hierarchy

0. **Country**: The sovereign state of Sri Lanka. National laws, taxation, defense, foreign policy, and countrywide administration are governed at this level.

1. **Province**: One of nine large administrative regions. Provinces have elected Provincial Councils responsible for education, health, local transport, and certain development functions.

2. **District**: One of 25 subdivisions of provinces. Districts are headed by District Secretaries who coordinate central government functions, disaster management, elections, and regional planning.

3. **Divisional Secretariat Division (DSD)**: Subdistrict administrative units led by Divisional Secretaries. They manage land administration, social welfare programs, permits, civil registrations, and coordination of village-level activities.

4. **Grama Niladhari Division (GND)**: The smallest government administrative unit with an appointed Grama Niladhari officer. Responsible for population records, household enumeration, certificates, dispute reporting, and acting as the state's representative at the community level.

5. **Village**: The smallest named settlement or locality. Villages do not have formal administrative power but are used in census work, local planning, election mapping, and community-level identification.

- **Note 1**: Zero indexing is used (Country=0) for consistency with most standard datasets.
- **Note 2**: While the administrative region **Village** exists, this repository does not include data about them. They are listed here for completeness.

## Region ID Structure

This repository uses codes defined by Sri Lanka's Department of Census and Statistics (DCS) as the primary key for every region. A region's code comprises its parent region's code followed by a numerical code. These segments reflect the nested administrative hierarchy and ensure consistent ordering.

The DCS coding system is similar to ISO 3166-2, first published in December 1998. Province codes are identical between the two systems, as are most district codes (except for the Northern Province). However, ISO 3166-2 only defines codes for provinces and districts, while the DCS system extends the hierarchy to include DSDs, GNDs, and villages.

### Example Regions and Codes

| Level    | ID Pattern         | Example                                             |
| -------- | ------------------ | --------------------------------------------------- |
| Country  | `LK`               | Sri Lanka `LK`                                      |
| Province | `LK-P`             | Western Province `LK-1`                             |
| District | `LK-P-D`           | Colombo District `LK-1-1` or `LK-11`                |
| DSD      | `LK-P-D-DSD`       | Thimbirigasyaya `LK-1-1-27` or `LK-1127`            |
| GND      | `LK-P-D-DSD-GND`   | Kollupitiya `LK-1-1-27-005` or `LK1127005`          |
| Village  | `LK-P-D-DSD-GND-V` | Rotunda Gardens `LK-1-1-27-005-02` or `LK-112700502` |

## 📚 Reference Sources

- Department of Census and Statistics, Sri Lanka: [https://www.statistics.gov.lk](https://www.statistics.gov.lk)
- Ministry of Public Administration: [https://pubad.gov.lk](https://pubad.gov.lk)
- ISO 3166 Online Browsing Platform (Sri Lanka LK): [https://www.iso.org/obp/ui/#iso:code:3166:LK](https://www.iso.org/obp/ui/#iso:code:3166:LK)
- ISO 3166-2 Standard Overview: [https://www.iso.org/iso-3166-country-codes.html](https://www.iso.org/iso-3166-country-codes.html)
- Wikipedia: ISO 3166-2 LK: [https://en.wikipedia.org/wiki/ISO_3166-2:LK](https://en.wikipedia.org/wiki/ISO_3166-2:LK)
- Wikipedia: Administrative divisions of Sri Lanka: [https://en.wikipedia.org/wiki/Administrative_divisions_of_Sri_Lanka](https://en.wikipedia.org/wiki/Administrative_divisions_of_Sri_Lanka)
- Administrative Districts Act (No. 22 of 1955): [https://survey.gov.lk/sdweb/pdf/surveydocuments/22%20of%201955.pdf](https://survey.gov.lk/sdweb/pdf/surveydocuments/22%20of%201955.pdf)

## Ground Truth Data Sources

- [Humanitarian Data Exchange](https://data.humdata.org) - Sri Lanka - Subnational Administrative Boundaries: [https://data.humdata.org/dataset/cod-ab-lka](https://data.humdata.org/dataset/cod-ab-lka)
- Department of Census and Statistics, Sri Lanka: [https://www.statistics.gov.lk](https://www.statistics.gov.lk)

## 📖 Appendix: Other Resources

- [A Brief History of Administrative Regions in Sri Lanka](README.history.md).

### [More Datasets about 🇱🇰 #SriLanka](https://github.com/nuuuwan/lk_datasets)

![Maintainer](https://img.shields.io/badge/maintainer-nuuuwan-red)
![MadeWith](https://img.shields.io/badge/made_with-python-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
