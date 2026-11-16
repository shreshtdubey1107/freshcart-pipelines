# FreshCart Pipelines

An end-to-end Data Engineering project covering Git and CI/CD, FreshCart ELT using Snowflake, Mage-based ML pipelines, and real-time streaming with RabbitMQ.

## Project Structure

- `elt/` - FreshCart ELT workflow
- `iris_project/` - Mage-based Iris classification pipeline
- `stream/` - RabbitMQ dispatcher and driver modules
- `tests/` - Automated test cases
- `.github/workflows/` - GitHub Actions CI configuration

## FreshCart ELT (Part B)

The Snowflake-based pipeline is managed through `elt.run_pipeline`. Configure the required Snowflake credentials and variables in `.env`, using `.env.example` as a reference template.

To execute the baseline pipeline with mock source data, run:

```powershell
python -m elt.run_pipeline --mode mock
```

Use `--mode transform-only` (the default mode) to execute transformations on previously loaded Bronze data without extracting or appending a new batch:

```powershell
python -m elt.run_pipeline --mode transform-only
```

To run a specific transformation stage independently, use the `--stage` option. For example, to execute the Gold stage:

```powershell
python -m elt.run_pipeline --stage gold
```

Pincode API responses are generated using deterministic mock data by default. To fetch actual responses, enable the `--live-pincodes` option. SQL transformation scripts are maintained in `elt/sql/`, while pure-Python business rule tests can be executed using `python -m pytest`.

Live data extraction requires the appropriate service URLs and authentication tokens, with the required variable names listed in `.env.example`.

Bronze file ingestion is managed through the additive migration `elt/sql/01_ingestion_files.sql`. Each ingestion record is identified using the SHA-256 hash of the normalized source and staged `source/date/filename` path. The compressed file's content checksum is also validated to ensure that modified files cannot silently reuse an existing identity.

Before executing PUT/COPY operations, the ingestion process creates a `LOADING` entry in the ledger. This status is updated to `LOADED` only after validating COPY results and verifying the corresponding Bronze source-file row counts. Unsuccessful attempts are marked as `FAILED` and can be retried.

In case of a process crash, an entry may remain in the `LOADING` state. Before manually updating its status, inspect the corresponding Bronze `SRC_FILE` row count and ensure that no other loader is currently active.

The ingestion ledger uses a standard Snowflake table for compatibility with trial accounts. Its `FILE_ID` column does not enforce uniqueness, so ingestion must operate in single-writer mode. A host-level lock prevents multiple local processes from running simultaneously; however, scheduled jobs and manual loaders must also be coordinated across different hosts to maintain a single active writer.

The loader detects duplicate ledger entries and blocks ambiguous legacy Bronze records that do not have corresponding ledger entries. Such records must be reconciled before attempting another ingestion.

Since Snowflake PUT, COPY, and ledger DML operations are executed separately rather than as a single atomic transaction, failed or interrupted ingestion attempts require the documented status and row-count verification process before being retried.

## Assignment Components

- Part A: Git and CI/CD Implementation
- Part B: FreshCart ELT Pipeline using Snowflake
- Part C: Machine Learning Pipeline with Mage
- Part D: Food Ordering Stream Processing with RabbitMQ
- Part E: Final Documentation, Report, and Viva