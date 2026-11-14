Executed by `sdd-devops`. [Actual receipt](docs/delivery/backup-and-release.md).

- **Backup:** `legacy-backup-8` completed; all 3 records passed integrity and byte-for-byte verification. Service, job, and routing were unchanged.
- **Recovery:** integrity verified; restore recoverability remains untested. Backup age cannot establish the required 15-minute recovery point.
- **Release:** readiness is blocked by mismatched revisions and missing final-candidate evidence. Explicit confirmation remains required.

No release endpoints, deployment, smoke, routing, restore, or retirement operations were performed.