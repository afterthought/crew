## REMOVED Requirements

### Requirement: Every merge into a bolt starts the bolt's verification
**Reason**: Once no worktree holds a bolt's branch, worktrunk runs a merge's post-merge hooks in the kit's main checkout, so crew's own post-merge verification no longer runs beside the bolt; crew verifies every kit's bolt the same way, from its declaration.
**Migration**: `kit-toolchain`'s "A bolt's head is verified through its kit's test adapter", with crew's `.config/sluice.toml` naming its required checks for bolt branches.

### Requirement: The bolt's verification is read for its head
**Reason**: The verification is crew's for every kit, read through crew rather than a script in crew's own repository.
**Migration**: `kit-toolchain`'s "A bolt's verification is read and run again through crew", by `crew bolt verify <bolt>`.

### Requirement: ops runs the verification again on the same head
**Reason**: As above.
**Migration**: `crew bolt verify <bolt> --again`, in `kit-toolchain`'s "A bolt's verification is read and run again through crew".
