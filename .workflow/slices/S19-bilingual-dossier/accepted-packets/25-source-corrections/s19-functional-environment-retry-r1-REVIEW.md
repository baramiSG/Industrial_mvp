# S19 functional environment retry review

**APPROVE the concrete stock-environment retry invocation**, bound to `s19/product-implementation-r1/r13-arabic-font/RETRY-COMMAND.txt` SHA256 `9c56627b5ca840d0c284eadd6beb923573a507439397dda734be36ad693319b7`. This is permission to test a stated environment hypothesis. It is not a root-cause finding, recovered-run PASS, acceptance of the failed attempt, or approval of unseen r14 product changes.

Preparation: reused full governing/authority preparation; read the complete failed/proposed command, retained RESOURCE-FAILURE-OBSERVATION, stock run_visual_baseline_container.py and visual_container.py, browser fixtures and affected harness/server/collector sections. After reading adopted browser-runtime reliability reviewer persona, invoked systematic-debugging and strict-reviewer, and applied Sanad/Muhasabah. No process, container, source, harness, test, or environment mutation by this reviewer.

## Observed failure and limits

Five retained trace ZIP checksums match the observation record. Direct raw trace inspection confirms two ERR_INSUFFICIENT_RESOURCES events followed by two Target crashed events. The retained post-crash process snapshot contains pytest and its Python application process but no Chromium process. The captured counters report memory.peak1,905,950,720bytes, zero cgroup OOM/OOM-kill and PID-limit events, /tmp344KB used of512MB and /dev/shm0 used of64MB. Because this snapshot is after the failure, it neither establishes nor excludes earlier temporary/shared-memory pressure or a userland allocator failure.

I directly inspected the complete captured combined stdout/stderr log (467bytes), its tail, the empty server.log and retained trace/network/log archive members: no Node/V8 heap-allocation or fatal-memory diagnostic was found. The captured evidence therefore supports browser resource failure/crash as the symptom; its precise exhausted resource remains unconfirmed. Do not report an OOM, /tmp-full or shm-full root cause as established.

The graceful-interruption record is for the explicitly owned `c532bee4e40d` pytest PID1 only. Its partial summary records839collected,121passed,6failed,0skipped,exit2. The original attempt remains **INCOMPLETE**, including its independent Arabic-font product failure and resource/crash symptoms. This review author performed no signal action and does not authorize broad process cleanup.

## Exact reviewed change

| Property | Failed invocation | Proposed retry |
|---|---|---|
| IPC | Docker default private IPC | Existing stock `--ipc=host` |
| Container temporary storage | Read-only container root plus `/tmp:rw,size=512m` tmpfs | Existing stock ordinary writable ephemeral container filesystem; omit those two custom restrictions |
| XDG cache | `/tmp` | Stock `/tmp/.cache` |
| Frozen source / output | r13 read-only source; owned r1 output | Separately accepted/frozen r14 read-only source; new owned r2 output |

The pinned image SHA256938b534c8bac0f80012299fc0bba33c00d29f2ade02416bbc1df9d9c028f8112, network-none, UID/GID1000, browser distribution, read-only `/workspace` source bind, sole host-writable `/proof` bind and trace/screenshot retention remain. No host network/PID mode, Docker socket, privileged mode, secret mount, dependency or harness change is introduced. Host IPC intentionally matches the already governed stock runner; it is not private IPC, and no IPC cleanup or unrelated-resource operation is authorized. The restored writable root is the disposable container filesystem, not the frozen source or another host path.

I parsed both recorded commands: their complete preflight plus full-functional pytest inner command is byte-identical, including `e2e and not visual`, failure traces/screenshots and explicit gate. Assertions, test selection and failure handling are not weakened. The stock harness continues to create/close each test context, run its same failure collector and retain owned server/summary output.

Execution prerequisites already in the accepted workflow: bind the actual independently accepted r14 source ledger before running this command (the future r14 directory did not yet exist at review time), preserve r1 unchanged, use fresh owned r2 output, and finish handling only the previously identified owned run under the coordinator's authority before starting a conflicting full run. This review does not require another routine owner approval or another environment review when those existing bindings are supplied. Any product delta approval remains separate.

The retry tests whether reverting the custom constrained IPC/temp setup to the proven stock execution pattern permits the full unchanged gate to complete. Since both settings return to that stock pattern together, success alone will not isolate which resource caused the previous crash. Failure must preserve actual logs/traces and advance diagnosis; it cannot be relabelled PASS or resolved by weakening tests.

Sanad: direct command/code reads, ZIP/hash verification and captured-log inspection; historical resource/process counters and signal outcomes are attributed to the retained records. The actual underlying resource hypothesis is explicitly unconfirmed. Risks/unverified: r14 source binding, retry execution/completion, exact failure cause and all required subsequent gates remain open. Muhasabah PASS for this bounded invocation review: no fabricated cause, no acceptance of an incomplete run, no broad process authority, and no new framework or product changes.
