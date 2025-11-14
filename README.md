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

This repository uses codes defined by Sri Lanka's Department of Census and Statistics (DCS) as the primary key for every region. A region's code comprises its parent region's code followed by a numerical code. These segments reflect the nested administrative hierarchy and ensure consistent ordering.

The DCS coding system is similar to ISO 3166-2, which was first published in December 1998. Province codes are identical between the two systems, as are most district codes (except for the Northern Province). However, ISO 3166-2 only defines codes for provinces and districts, while the DCS system extends the hierarchy to include districts, DSDs, GNDs, and villages.

### Example Regions and Codes

| Level    | ID Pattern         | Example                                             |
| -------- | ------------------ | --------------------------------------------------- |
| Country  | `LK`               | Sri Lanka `LK`                                      |
| Province | `LK-P`             | Western Province `LK-1`                             |
| District | `LK-P-D`           | Colombo District `LK-1-1` or `LK-11`                |
| DSD      | `LK-P-D-DSD`       | Thimbirigasyaya `LK-1-1-27` or `LK-1127`            |
| GND      | `LK-P-D-DSD-GND`   | Kollupitiya `LK-1-1-27-005` or `LK1127005`          |
| Village  | `LK-P-D-DSD-GND-V` | Rotunda Gardens `LK-1-1-27-005-02` or `LK112700502` |


## Brief History of Administrative Regions in Sri Lanka


### 1833

Following the recommendations of the Colebrooke-Cameron Commission, five provinces under one administration came into being:

- Western Province (LK-1) – The maritime districts of Colombo, Chilaw and Puttalam, and the Kandyan provinces of Three Korales, Four Korales, Seven Korales and Lower Bulathgama.
- Central Province (LK-2) – The central Kandyan Provinces.
- Southern Province (LK-3) – The maritime districts of Galle, Hambantota, Matara and Tangalle, and the Kandyan provinces of Lower Uva, Saffragam and Wellassa.
- Northern Province (LK-4) – The maritime districts of Jaffna, Mannar and Vanni, and the Kandyan province of Nuwara Kalawiya.
- Eastern Province (LK-5) – The maritime districts of Batticaloa and Trincomalee, and the Kandyan provinces of Bintenna and Tamankaduwa.

### 1845 to 1889

Since, 4 additional provinces were created by carving out parts of existing provinces.

- North Western Province (LK-6) – Created in 1845 from northern parts of the Western Province (the districts of Chilaw, Puttalam and Seven Korales).
- North Central Province (LK-7) – Created in 1873 from southern parts of the Northern Province (district of Nuwara Kalawiya) and north western parts of the Eastern Province (district of Tamankaduwa).
- Uva Province (LK-8) – Created in 1886 from parts of the Central Province, Eastern Province (district of Bintenna) and Southern Province (district of Wellassa).
- Sabaragamuwa Province (LK-9) – Created in 1889 from modern day Ratnapura District, which was part of the Southern Province, and Kegalle, which was part of the Western Province.

## 1955

The Administrative Districts Act (No. 22 of 1955) took effect on 14 April 1955, formally defining the following 21 administrative districts of Sri Lanka:

- Colombo (LK-11)  ￼
- Kalutara (LK-13)  ￼

- Kandy (LK-21)  ￼
- Matale (LK-22)  ￼
- Nuwara Eliya (LK-23)  
￼
- Galle (LK-31)  ￼
- Matara (LK-32)  ￼
- Hambantota (LK-33)  ￼

- Jaffna (LK-41)  ￼
- Mannar (LK-43)  ￼
- Vavuniya (LK-44) 
 ￼
- Batticaloa (LK-51)  ￼
- Ampara (LK-52)  ￼
- Trincomalee (LK-53)  ￼

- Kurunegala (LK-61)  ￼
- Puttalam (LK-62)  ￼

- Anuradhapura (LK-71)  ￼
- Polonnaruwa (LK-72)  ￼

- Badulla (LK-81)  ￼

- Ratnapura (LK-91)  ￼
- Kegalle (LK-92)  ￼

## 1978



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
- Administrative Districts Act (No. 22 of 1955) - [https://survey.gov.lk/sdweb/pdf/surveydocuments/22%20of%201955.pdf](https://survey.gov.lk/sdweb/pdf/surveydocuments/22%20of%201955.pdf)

