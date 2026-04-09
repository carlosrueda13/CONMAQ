# API Service

Backend service responsible for exposing contracts and supplier matching.

## Runtime modes

### Demo mode

Activated when no DATABASE_URL or SECOP_DATA_SOURCE exists.

Returns mock contracts so frontend can function.

### Real mode

Activated when environment variables exist.

Reads contracts from database populated by SECOP datasets.

## Example endpoint

GET /contracts

Returns:

{
 id,
 entity,
 value,
 location,
 sector
}

## TODO

- Implement NestJS server
- Add Postgres connection
- Add SECOP ingestion adapter
