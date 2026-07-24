# krack-frag-probe(1) — educational Wi-Fi regression tester

## NAME

krack-frag-probe — lab-only regression tester for long-patched Wi-Fi edge cases

## SYNOPSIS

```
krack-frag-probe list-tests [--verbose]
krack-frag-probe run --iface IFACE --bssid BSSID [options]
krack-frag-probe report --input FILE [--format html|md|json]
```

## DESCRIPTION

**krack-frag-probe** is an educational, **defensive** regression tester. It
crafts minimal 802.11 lab frames (via Scapy) to check whether modern drivers and
firmware still correctly handle edge cases related to historical KRACK-style and
FragAttacks-style issues.

**Bold: authorized laboratory use only** on equipment you own or have written
permission to test. Not an exploit toolkit. No automated scanning of unknown
networks.

## SAFETY

Before any non-dry-run transmission the operator must acknowledge:

```
I UNDERSTAND AND ACCEPT
```

Live runs require a **monitor-mode** interface and an **explicit** BSSID.

## OPTIONS (run)

See `krack-frag-probe run --help`.

## EXIT STATUS

- 0 — all tests passed  
- 1 — one or more failures  
- 2 — configuration or permission error  

## AUTHOR

**Kirtan Teg Singh** (romanized) / **ਕੀਰਤਨ ਤੇਗ ਸਿੰਘ** (Gurmukhi / ਗੁਰਮੁਖੀ).

## SEE ALSO

docs/lab-setup.md, docs/ethics-and-warnings.md, SECURITY.md, AUTHORS.md

## BUGS

Report issues via the project tracker. Do not request weaponization features.
