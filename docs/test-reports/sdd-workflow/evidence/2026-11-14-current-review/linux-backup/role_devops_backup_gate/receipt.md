The `sdd-devops` role completed the work. [Actual receipt](docs/delivery/backup-and-release.md).

- Backup `legacy-backup-8` succeeded; verification passed for all three records.
- No service or routing impact. A later backup can overwrite the fixed backup file. Recovery remains unproven until an authorized restore and dependency check pass.
- Release 2.4.0 is not ready: final-candidate post-refactor integration evidence and explicit release confirmation are missing.

No release endpoints, deployment, smoke, routing, restore or retirement were invoked.