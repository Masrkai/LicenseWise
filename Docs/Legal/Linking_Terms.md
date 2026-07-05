# Linking Terms

How software components are connected and what license implications follow.

## Linking Methods

| Term | Plain Explanation | License Implications |
|------|-------------------|---------------------|
| **Static Linking** | Combining the library code directly into your program at compile time. The library becomes part of your executable. | With LGPL, this may require the combined work to also be LGPL. |
| **Dynamic Linking** | Connecting to the library at runtime rather than compile time. The library remains a separate file. | With LGPL, dynamic linking is generally safe for proprietary apps. |

## Combined Works

| Term | Plain Explanation | License Implications |
|------|-------------------|---------------------|
| **Combined Work** | A work that incorporates code from multiple sources. Copyleft licenses may require the entire combined work to be licensed under the same terms. | Strong copyleft (GPL) requires entire combined work to be GPL |
| **Linked Code** | Code that has been connected to other code through linking. GPL copyleft may "infect" linked code. | GPL copyleft can "infect" linked code |
| **Module** | In EPL, copyleft applies per "module" rather than per file. A module is a logically separable unit of code. | EPL-2.0 uses module-level copyleft |

## Copyleft Spread

| Term | Plain Explanation | Which Licenses? |
|------|-------------------|-----------------|
| **Viral** | Informal term for licenses like AGPL where copyleft "spreads" to any code that interacts with the licensed software, similar to how a virus spreads. | AGPL-3.0 (most aggressive) |
| **Infection** | Informal term for how copyleft licenses can "infect" other code when combined or linked. | GPL, AGPL |
| **SaaS Loophole** | The gap in traditional copyleft licenses where SaaS use does not trigger copyleft because no "distribution" occurs. AGPL closes this loophole. | AGPL-3.0 closes this |

## Practical Examples

| Scenario | License Impact |
|----------|----------------|
| Proprietary app dynamically links to LGPL library | Generally allowed; library must remain LGPL |
| Proprietary app statically links to LGPL library | May require entire app to be LGPL |
| GPL library linked into proprietary app | Entire app must be GPL (strong copyleft) |
| AGPL library used as network service | Must provide source to all users (network copyleft) |
| MPL-2.0 file modified and combined with proprietary code | Modified MPL file must stay MPL; new files can be proprietary |

## See Also

- [License_Classification](License_Classification.md) - Strong vs. weak copyleft explained
- [Distribution_Terms](Distribution_Terms.md) - How linking triggers distribution conditions
- [Compatibility](Compatibility.md) - Which licenses can be combined
