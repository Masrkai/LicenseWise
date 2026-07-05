# Business Models and Licensing

How open-source and commercial licensing intersect in business.

## Licensing Models

| Term | Plain Explanation | How It Works |
|------|-------------------|--------------|
| **Dual Licensing** | Offering the same software under two different licenses (e.g., GPL + commercial). The copyleft license enables this model by requiring anyone who cannot comply with copyleft to purchase a commercial license. | Users choose: comply with GPL (free) or buy commercial license (proprietary use) |
| **CLA** (Contributor License Agreement) | A legal agreement between a contributor and the project that grants the project maintainer certain rights over the contributed code, enabling dual licensing. | Contributors sign CLA; project can relicense contributions |
| **Commercial License** | A paid license that allows use under terms different from the open-source license. | Typically removes copyleft, adds support/warranty |
| **Open-Core** | A business model where the core software is open source, but additional features or services are available under a commercial license. | Core = open source; extras = commercial |

## Source Disclosure Business Impact

| Term | Plain Explanation | Business Implication |
|------|-------------------|---------------------|
| **Source Disclosure Requirement** | When a license (like GPL) requires you to share your source code with anyone you distribute the software to. | Competitors can see your code if you distribute |
| **SaaS Loophole** | The gap in traditional copyleft licenses where SaaS use does not trigger copyleft because no "distribution" occurs. | Allows SaaS without sharing source (except AGPL) |
| **AGPL Network Copyleft** | AGPL closes the SaaS loophole by requiring source disclosure for network use. | SaaS providers must share source with users |

## Proprietary vs. Open Source

| Term | Plain Explanation | Business Context |
|------|-------------------|------------------|
| **Proprietary** | Software where the owner retains all rights. No permission to use, copy, modify, or distribute without explicit authorization. | Traditional commercial software model |
| **Source-Available** | Software where the source code is accessible but the license does not meet the Open Source Definition. May restrict commercial use, SaaS, or other activities. | Middle ground: see code but with restrictions |
| **Open Source** | Software released under a license that allows anyone to use, modify, and distribute the code, meeting the Open Source Definition maintained by OSI. | Community-driven development model |

## License Choice for Businesses

| Business Need | Recommended License Type |
|---------------|-------------------------|
| Maximum adoption | Permissive (MIT, Apache) |
| Ensure contributions stay open | Copyleft (GPL, AGPL) |
| Dual licensing revenue | Strong copyleft (GPL) + commercial |
| Prevent SaaS competition | AGPL-3.0 |
| File-level control | MPL-2.0, EPL-2.0 |
| Complete proprietary | BSL-1.0, Elastic-2.0 |

## See Also

- [License_Classification](License_Classification.md) - Understanding copyleft strength
- [Compatibility](Compatibility.md) - Combining licenses in projects
- [Compliance](Compliance.md) - Following license requirements
