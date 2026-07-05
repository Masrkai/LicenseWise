# Legal Terms Documentation Index

A comprehensive glossary of legal terms used throughout LicenseWise, organized by category.

## Documentation Structure

| File | Contents | Key Terms |
|------|----------|-----------|
| [License_Types.md](License_Types.md) | All supported software licenses | GPL, MIT, Apache, BSD, CC-BY, etc. |
| [License_Classification.md](License_Classification.md) | How licenses are categorized | Permissive, Copyleft, Strong/Weak, Open Source |
| [Legal_Concepts.md](Legal_Concepts.md) | Core legal rights and protections | Copyright, Patent, Liability, Warranty |
| [Distribution_Terms.md](Distribution_Terms.md) | How software is shared | Distribution, Source Disclosure, SaaS |
| [Linking_Terms.md](Linking_Terms.md) | Software integration concepts | Static/Dynamic Linking, Combined Work |
| [Business_Models.md](Business_Models.md) | Commercial licensing models | Dual Licensing, CLA, Open-Core |
| [Compatibility.md](Compatibility.md) | License compatibility rules | Compatible, Incompatible, One-Way |
| [Standards.md](Standards.md) | Organizations and standards | OSI, FSF, SPDX |
| [Jurisdiction.md](Jurisdiction.md) | Legal validity across regions | Jurisdiction, Legal Recognition |
| [Compliance.md](Compliance.md) | Following license requirements | Compliance, Violations, Disclaimers |

## Quick Reference

### Most Common Terms

| Term | Definition |
|------|------------|
| **Copyleft** | Requires derivative works to use the same license |
| **Permissive** | Allows almost any use with minimal requirements |
| **Attribution** | Must give credit to original author |
| **Source Disclosure** | Must share source code when distributing |
| **Derivative Works** | Any work based on the original |
| **SaaS** | Software as a Service (network use) |
| **SPDX** | Standard license identifier format |

### License Strength Spectrum

```
Weakest                                              Strongest
  |                                                      |
  v                                                      v
Public Domain -> Permissive -> Weak Copyleft -> Strong Copyleft -> AGPL
  (Unlicense)     (MIT)         (MPL, LGPL)      (GPL)          (Network)
```

### Common License Choices

| Need | Recommended License |
|------|---------------------|
| Maximum adoption | MIT or Apache-2.0 |
| Patent protection + no document changes | BlueOak-1.0.0 |
| Keep contributions open | GPL-3.0 |
| Prevent SaaS competition | AGPL-3.0 |
| File-level control | MPL-2.0 |
| Library linking flexibility | LGPL-3.0 |
| Public domain | CC0-1.0 |
| EU government project | EUPL-1.2 |

## About LicenseWise

LicenseWise is a tool that helps developers choose the right license for their projects by asking questions about their needs and preferences. It uses a Prolog-based rule engine to analyze answers and recommend suitable licenses.

**Disclaimer**: LicenseWise provides educational information, not legal advice. Always consult a qualified lawyer for legal decisions.

## See Also

- [APIs.md](../APIs.md) - External license data sources
- [QuickTestGuide.md](../QuickTestGuide.md) - Testing LicenseWise
