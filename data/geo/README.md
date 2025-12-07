# Geo Data

## Regions

This repository contains geographic information for five levels of administrative regions:

0. Country
1. Province
2. Administrative District
3. Divisional Secretariat Division (DSD)
4. Grama Niladhari Division (GND)

To avoid violating GitHub's file size limits, files **exceeding 20MB** have been excluded from this repo.

## File Formats

The geographic data is represented in three file formats:

- **GeoJSON**: A widely used format for encoding geographic data structures, containing features with geometry (points, lines, polygons) and properties.
- **TopoJSON**: An extension of GeoJSON that encodes topology, ensuring shared boundaries between regions are stored efficiently and consistently.
- **Plain JSON MultiPolygons**: A simplified representation of geographic data, where only the coordinates of MultiPolygon geometries are stored without additional metadata.

## Precision Levels

Geographic data is available at five levels of precision, depending on the use case:

- **Original**: Unmodified geographic data as obtained from the source.
- **Small**: Simplified to a precision of 0.0001 degrees (suitable for high-detail applications).
- **Smaller**: Simplified to a precision of 0.001 degrees (suitable for medium-detail applications).
- **Smallest**: Simplified to a precision of 0.01 degrees (suitable for low-detail applications).
- **Smallestest**: Simplified to a precision of 0.1 degrees (suitable for very low-detail applications, such as overviews or large-scale maps).

Each level of precision balances file size and detail, making it easier to choose the appropriate format for specific tasks, such as visualization, analysis, or data sharing.
