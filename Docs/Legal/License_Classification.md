# License Classification

How software licenses are categorized based on their requirements and restrictions.

## Primary Classifications

| Term | Plain Explanation | Examples | Key Characteristic |
|------|-------------------|----------|-------------------|
| **Permissive** | Allows almost any use with minimal requirements (usually just retain the copyright notice). | MIT, BSD, Apache-2.0, ISC | Maximum freedom for users |
| **Copyleft** | Requires derivative works to be released under the same license, ensuring software remains free for all future users. | GPL, AGPL | "Share-alike" requirement |
| **Proprietary** | Owner retains all rights. No permission to use, copy, modify, or distribute without explicit authorization. | Commercial software | All rights reserved |
| **Public Domain** | No copyright restrictions at all. Anyone can do anything with the work without any conditions. | Unlicense, CC0 | No restrictions |

## Copyleft Spectrum

Copyleft licenses exist on a spectrum from strong to weak:

| Term | Plain Explanation | Scope | Examples |
|------|-------------------|-------|----------|
| **Strong Copyleft** | Any derivative or combined work must also be released under the same copyleft license. | Entire combined work | GPL-2.0, GPL-3.0, AGPL-3.0 |
| **Weak Copyleft** | Only applies to the specific library or file, not the entire combined work. Proprietary software can use it if they don't modify the copyleft portions. | Library or file only | LGPL, MPL-2.0, EPL-2.0 |
| **File-level Copyleft** | Copyleft applies only to individual files. Only modified files must remain under the copyleft license; new files can use any license. | Individual files | MPL-2.0 |
| **Library-level Copyleft** | Copyleft applies to a library specifically. The library must stay open, but applications linking to it can be proprietary. | The library | LGPL |
| **Network Copyleft** | Copyleft triggered by network interaction (not just distribution). If users access the software over a network, they must be given source access. | Network use | AGPL-3.0 |

## Other Classifications

| Term | Plain Explanation | Examples |
|------|-------------------|----------|
| **Open Source** | Software released under a license that allows anyone to use, modify, and distribute the code, meeting the Open Source Definition maintained by OSI. | MIT, GPL, Apache |
| **Free Software** | Software that respects users' four essential freedoms: run the program, study/change it, redistribute copies, and distribute modified versions. Defined by the FSF. | GPL, MIT (FSF considers it free) |
| **Source-Available** | Software where the source code is accessible but the license does not meet the Open Source Definition. May restrict commercial use, SaaS, or other activities. | BSL-1.0, Elastic-2.0 |

## Classification Overlap

Many licenses fit multiple categories:

| License | Permissive? | Copyleft? | Open Source? | Free Software? |
|---------|-------------|-----------|--------------|----------------|
| MIT | Yes | No | Yes | Yes |
| GPL-3.0 | No | Strong | Yes | Yes |
| LGPL-3.0 | No | Weak | Yes | Yes |
| MPL-2.0 | No | File-level | Yes | Yes |
| AGPL-3.0 | No | Network | Yes | Yes |
| CC-BY-4.0 | Yes | No | N/A (content) | N/A (content) |
| CC-BY-NC-4.0 | No | No | N/A (content) | N/A (content) |
| Unlicense | Yes | No | Yes | Yes |
| BSL-1.0 | No | No | No | No |

## See Also

- [License Types](License_Types.md) - All supported licenses
- [Distribution_Terms](Distribution_Terms.md) - How copyleft is triggered
- [Compatibility](Compatibility.md) - Which licenses can be combined
