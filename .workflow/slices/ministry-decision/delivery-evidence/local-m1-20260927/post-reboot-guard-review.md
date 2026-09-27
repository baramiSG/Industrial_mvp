**Verdict: APPROVE the post-reboot guard amendment**, SHA-256 `af2fce4f5962d867f8cf2c480e4e48e32f9aecbce365abfc79ceec4942e32a1d`, with the binding conditions below. This is an operational guard change only. It does not approve M1, any gate result or live Aura. All checks were read-only; no locks, services, Git or secrets were touched.

## Verified directly

- **The reboot is real, and the old identity can't be satisfied.**
  - `uptime -s` reads `2026-09-26 23:18:36`, matching `RECOVERY.json` (`kernel_boot_utc` 23:18:36Z). The current `boot_id` is `8471bf0e-e7b9-4771-90df-8193de076675`.
  - `ps -p 34210` returns no process.
  - The existing executor guard is literal (`EXECUTE-M-ONE-GATE-G1-3.py:17`: `/proc/34210/stat … == '79799'`). It can never pass again, so replacing it is necessary.
- **Same lease file, no holder.**
  - `delivery.lock` has inode 2358670, device 2096, 0 bytes, mode 644, mtime 2026-09-16, unchanged.
  - `/proc/locks` has no row for inode 2358670. The earlier record's `08:30:2358670` corresponds to device 8×256+48 = 2096, so it is the same file.
  - The executor's inode guard (line 18) stays valid.
- **Retained graph intact.**
  - `RETAINED-GRAPH.json` and `retained-verify.stdout` show `GRAPH VERIFY PASS`: 461bf, 925 nodes / 1045 edges, 410 public / 515 synthetic, partitions and provenance valid.
  - `RETAINED-IDENTITY.json` shows the same full container ID 42216eec…, running and healthy. The non-Env config hash `ac70bfd8…` is the same. The mounts are the same set; only their order differs. NetworkID, IP, gateway and aliases are unchanged; only the EndpointID and MAC changed.
  - `RECOVERY.json` shows zero W source changes and all 64 protected indexes unchanged.
- **The existing mechanism is reused.** `owner-decisions/s16b-delivery-acceptance-1.json` records a native `flock` on `delivery.lock`, held through the delivery receipt. No new protocol is introduced.

## Binding conditions

1. **Dedicated holder that nothing inherits.** Acquire `LOCK_EX|LOCK_NB` from a minimal, dedicated holder process on a file descriptor that is non-inheritable (close-on-exec). The gate executor and its `make`/Docker children must not inherit it. After acquisition, verify that `/proc/locks` shows exactly one `FLOCK ADVISORY WRITE <holderPID> 08:30:2358670` row, with no other holder. Any contention or unexpected row means STOP. Never unlink, truncate, rewrite, chmod or unlock another holder.
2. **Replaced guard is a complete identity check.** Line 17 becomes the recorded holder PID plus its `/proc/<pid>/stat` start ticks, plus boot ID equal to `8471bf0e-…`, plus a `/proc/locks` owner row matching PID, device and inode. Check this immediately before the operation, before each mutating phase, and before and after recovery. A missing holder, a changed boot ID or a replaced inode means STOP before any new mutation. Record the exact adapted executor diff and its hash before execution.
3. **Honest records.** Write a successor ownership record that cites the verified reboot. It must state that 34210/79799 ended with the kernel reboot and that its exit is unknown, and it must leave `20260926-ministry-ma3-aura-continuation-acceptance-1.json` and all historical receipts unchanged.
4. **Everything else unchanged.** Keep the literal 461bf/925/1045/partition checks, the mount multiset and non-Env config checks, stable network fields, quiet-window, reader, port and resource guards, a fresh single-run namespace, the external 1G heap, the original 2 s / no-retry tests, `down` without `-v`, same full-ID restoration and index preservation. Close only the holder's own lease at final release. If the holder is lost during an owned operation, apply only the already approved, attributable owned cleanup and exact retained recovery, with no gate rerun.

**Scope:** this successor binding may be reused for later M-A3 GO preparation. M-A3 still needs the delivered-subject binding, fresh preflight and exact-pair recovery, and its own concrete operational GO review.

**Muhasabah: PASS.** The boot, lock, retained-identity and executor-guard facts were read directly. The new holder's identity and outcomes remain prospective.
