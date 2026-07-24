# Ethics and warnings

## Mission

**krack-frag-probe** exists to help researchers, educators, and vendors verify
that **already-public, long-patched** Wi-Fi edge-case fixes (KRACK-style key
reinstallation handling and FragAttacks-style fragmentation/aggregation
handling) remain effective on **new** drivers, chips, and firmware.

## Non-negotiable rules

1. **Authorization first.** Only test equipment you own or have **written**
   permission to test.
2. **No weaponization.** Do not add exploit chains, scanners for unknown
   networks, credential theft, or RCE.
3. **No zero-day claims.** A FAIL under lab conditions is a *regression signal*
   to investigate—not a public vulnerability brand without responsible process.
4. **Minimal frames.** Send only what is needed for the educational probe.
5. **Transparency.** Preserve legal banners, acknowledgements, and safety gates.

## Why the legal prompt exists

Wireless injection can disrupt networks and may be illegal without permission.
The phrase `I UNDERSTAND AND ACCEPT` creates a deliberate pause so operators
cannot claim they “just ran a script” without seeing the warning.

## Responsible disclosure if you believe you found a regression

1. Confirm in an isolated lab with multiple trials.
2. Notify the vendor privately with evidence and environment details.
3. Do not publish exploit-ready instructions.
4. Coordinate timelines with the vendor and any relevant CERT.

## Academic and classroom use

Instructors should:

- Provide dedicated lab APs and adapters
- Prohibit off-campus or third-party targeting
- Grade dry-run and report quality, not “successful attacks”
- Use `--simulate-regression` for demoing FAIL report formatting without RF

## Relationship to public research

Public papers and advisories on KRACK and FragAttacks describe historical bugs.
This tool **does not reimplement those exploits**. It only exercises related
edge-handling paths with benign lab markers so modern stacks can be
regression-checked.

## Consequences of misuse

Misuse may result in:

- Criminal and civil liability
- Expulsion from academic programs
- Ban from this project’s community spaces
- Reporting to hosting platforms and employers where required

## Operator pledge (recommended)

> I will only use krack-frag-probe on systems I am authorized to test.  
> I will not attempt to weaponize or redistribute this software for attacks.  
> I understand this is a defensive educational regression tester.

**LAB ONLY – NOT FOR PRODUCTION USE**
