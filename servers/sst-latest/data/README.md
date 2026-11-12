# Data card: sst-latest

The server bundles no data. The only files are five small test fixtures in `tests/data/`. Maps, GIFs and fetched subsets go to `sst_output/`, which is git-ignored.

| File | What it contains | Units | Class | Source | License |
|---|---|---|---|---|---|
| `tests/data/cmr_collections_mur.json` | One CMR collection record (id, title, short name, version), trimmed | none | cached live response | `https://cmr.earthdata.nasa.gov/search/collections.json?concept_id=C1996881146-POCLOUD` | NASA open metadata |
| `tests/data/cmr_granules_mur.json` | The newest granule record of that collection (name, start, end, id), trimmed | none | cached live response | `https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C1996881146-POCLOUD&sort_key=-start_date&page_size=1` | NASA open metadata |
| `tests/data/erddap_sst_2026-11-09.csv`, `erddap_sst_2026-11-10.csv` | Real MUR analysed SST, 4 x 4 degree box off California, 0.5 degree grid (81 points, 32 land) | degC | cached live response | NOAA CoastWatch ERDDAP `jplMURSST41`, `analysed_sst[(2026-11-10T09:00:00Z)][(33):50:(37)][(-123):50:(-119)]` | open data |
| `tests/data/erddap_times.csv` | The ten newest daily time stamps of that dataset | none | cached live response | `jplMURSST41.csv?time[last-9:1:last]` | open data |

## Provenance

- Retrieved from the public CMR search API and NOAA ERDDAP on 2026-11-12 with no credentials; fields not used by the tests were removed.
- Dataset: GHRSST Level 4 MUR Global Foundation Sea Surface Temperature Analysis, v4.1 (`C1996881146-POCLOUD`).

## Redistribution

The CMR files hold only catalog metadata. The ERDDAP files hold a few dozen SST values for a small box; the source is openly published and the files are about 3 KB each, far below the 1 MB limit.
