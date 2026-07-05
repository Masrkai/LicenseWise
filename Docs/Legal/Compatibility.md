# License Compatibility

Whether two licenses can be combined in a single project without legal conflict.

## Compatibility Basics

| Term | Plain Explanation | Why It Matters |
|------|-------------------|----------------|
| **Compatible** | When two licenses can be combined in a single project without their terms contradicting each other. | Allows using multiple libraries in one project |
| **Incompatible** | When two licenses cannot be combined because their terms contradict each other (e.g., GPL-2.0 and Apache-2.0). | Prevents using certain libraries together |
| **One-Way Compatibility** | When license A can be incorporated into license B, but not vice versa. GPL-3.0 added one-way compatibility with Apache-2.0. | GPL-3.0 projects can use Apache-2.0 code, but not reverse |

## Common Compatibility Scenarios

| License A | License B | Compatible? | Notes |
|-----------|-----------|-------------|-------|
| MIT | Apache-2.0 | Yes | Both permissive; easy to combine |
| GPL-2.0 | Apache-2.0 | No | GPL-2.0 is incompatible with Apache-2.0 patent clauses |
| GPL-3.0 | Apache-2.0 | One-way | GPL-3.0 can include Apache-2.0, but not reverse |
| GPL | MIT | Yes | MIT is compatible with GPL |
| MPL-2.0 | GPL | Yes | MPL-2.0 includes GPL compatibility clause |
| EPL-2.0 | GPL | Yes | EPL-2.0 includes GPL compatibility clause |
| LGPL | GPL | Yes | LGPL can be upgraded to GPL |
| AGPL | GPL | No | Network copyleft vs. distribution copyleft |

## Detection and Resolution

| Term | Plain Explanation | How LicenseWise Handles It |
|------|-------------------|---------------------------|
| **Contradiction Detection** | Logic that detects when a user's choices conflict (e.g., wanting both public domain and copyleft). | LicenseWise Prolog rules detect conflicts |
| **Infection** | Informal term for how copyleft licenses can "infect" other code when combined or linked. | Considered when recommending licenses |
| **SaaS Loophole** | The gap in traditional copyleft licenses where SaaS use does not trigger copyleft because no "distribution" occurs. AGPL closes this loophole. | LicenseWise asks about SaaS to avoid this |

## Compatibility Rules of Thumb

1. **Permissive + Permissive** = Always compatible
2. **Permissive + Copyleft** = Compatible (permissive can be included in copyleft)
3. **Copyleft + Copyleft** = Must be same strength (GPL + GPL = OK; GPL + AGPL = problematic)
4. **Strong Copyleft + Weak Copyleft** = Weak can be upgraded to strong
5. **Any + Proprietary** = Never compatible (proprietary restricts rights)

## See Also

- [License_Classification](License_Classification.md) - Understanding copyleft strength
- [Linking_Terms](Linking_Terms.md) - How linking affects compatibility
- [Standards](Standards.md) - OSI and FSF compatibility lists
