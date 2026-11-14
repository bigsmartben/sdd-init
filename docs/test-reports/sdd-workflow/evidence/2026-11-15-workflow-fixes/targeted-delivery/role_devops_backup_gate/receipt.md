The sdd-devops role completed the work and wrote the [actual receipt](docs/delivery/backup-and-release.md).

- **Backup:** `legacy-backup-8` completed with all 3 records.
- **Verification:** Passed byte-for-byte comparison and SHA-256 matching.
- **Recovery conditions:** Restore remains untested; recovery requires an authorized restore plus record and dependency verification. A future backup overwrites the fixed backup file.
- **Release 2.4.0:** Blocked by integration evidence for an earlier revision, missing separate source attestation, and pending explicit confirmation.

No release simulator endpoints, deploy, smoke, route, restore, or retire actions were performed.