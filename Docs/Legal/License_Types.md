# License Types Reference

A comprehensive list of all software licenses supported by LicenseWise, with plain-language explanations.

## GNU Family

| License | Full Name | Plain Explanation |
|---------|-----------|-------------------|
| **GPL-2.0** | GNU General Public License v2.0 | Strong copyleft. Any derivative work must be released under GPL-2.0. Used by the Linux kernel. |
| **GPL-3.0** | GNU General Public License v3.0 | Updated GPL with anti-tivoization protections and explicit patent grants. |
| **LGPL-2.1** | GNU Lesser General Public License v2.1 | Weak copyleft. Allows proprietary software to link against the library, but modifications to the library itself must be shared. |
| **LGPL-3.0** | GNU Lesser General Public License v3.0 | Updated LGPL with GPL-3.0 protections including anti-tivoization and patent terms. |
| **AGPL-3.0** | GNU Affero General Public License v3.0 | Extends GPL-3.0 with network-use copyleft. If users interact over a network, they must be given source access. |

## Permissive Licenses

| License | Full Name | Plain Explanation |
|---------|-----------|-------------------|
| **MIT** | MIT License | Short, permissive license. Only requirement: retain the copyright notice. |
| **MIT-0** | MIT No Attribution License | Same as MIT but without the attribution requirement. |
| **Apache-2.0** | Apache License 2.0 | Permissive license with explicit patent grant and protection against contributor patent claims. |
| **BSD-2-Clause** | BSD 2-Clause "Simplified" License | Similar to MIT; requires attribution in source and binary distributions. |
| **BSD-3-Clause** | BSD 3-Clause "New" or "Revised" License | BSD-2-Clause plus a non-endorsement clause (cannot use project name for promotion). |
| **ISC** | ISC License | Functionally equivalent to MIT/BSD-2-Clause but shorter. Default for many npm packages. |
| **PostgreSQL** | PostgreSQL License | Short permissive license similar to MIT/BSD, used exclusively by the PostgreSQL project. |
| **Artistic-2.0** | Artistic License 2.0 | Permissive with optional copyleft clause for modified standard versions. Used by Perl and Raku. |
| **Zlib** | zlib License | Very permissive; modified versions must be marked as changed and cannot be misrepresented as original. Common in game development. |

## Weak Copyleft

| License | Full Name | Plain Explanation |
|---------|-----------|-------------------|
| **MPL-2.0** | Mozilla Public License 2.0 | File-level copyleft. Modified MPL files must remain open, but can be combined with proprietary code. |
| **EPL-2.0** | Eclipse Public License 2.0 | File-level weak copyleft. Modifications to EPL files must be shared. Includes patent grant. |
| **CDDL-1.0** | Common Development and Distribution License 1.0 | File-level copyleft from Sun Microsystems. Used for OpenSolaris and ZFS. Incompatible with GPL. |

## Public Domain

| License | Full Name | Plain Explanation |
|---------|-----------|-------------------|
| **Unlicense** | The Unlicense | Dedicates software to the public domain. No restrictions whatsoever. May not be valid in all jurisdictions. |
| **CC0-1.0** | Creative Commons Zero v1.0 Universal | Public domain dedication with fallback permissive license for jurisdictions that don't recognize public domain waivers. |

## Creative Commons

| License | Full Name | Plain Explanation |
|---------|-----------|-------------------|
| **CC-BY-4.0** | Creative Commons Attribution 4.0 International | Any use including commercial, with attribution required. Designed for creative works, not software. |
| **CC-BY-NC-4.0** | Creative Commons Attribution-NonCommercial 4.0 International | Non-commercial purposes only, with attribution. |
| **CC-BY-SA-4.0** | Creative Commons Attribution-ShareAlike 4.0 International | Attribution required; derivatives must use the same license. Wikipedia uses this. |
| **CC-BY-NC-SA-4.0** | Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International | Non-commercial only; derivatives must use the same license. Most restrictive standard CC license. |
| **ODbL** | Open Database License 1.0 | Copyleft for databases. Used by OpenStreetMap. |

## Regional

| License | Full Name | Plain Explanation |
|---------|-----------|-------------------|
| **EUPL-1.2** | European Union Public Licence 1.2 | Copyleft designed for EU public sector software. Legally valid across all EU jurisdictions. |

## Source-Available / Proprietary

| License | Full Name | Plain Explanation |
|---------|-----------|-------------------|
| **BSL-1.0** | Business Source License 1.1 | Source-available but not open source. Restricts production use until a Change Date, then converts to an open-source license. |
| **Elastic-2.0** | Elastic License 2.0 | Source-available. Prohibits providing as a managed service and circumventing license key restrictions. |
| **Proprietary** | All Rights Reserved | No rights granted beyond what the license explicitly states. Default copyright law applies. |

## See Also

- [License Classification](License_Classification.md) - How licenses are categorized by behavior
- [Compatibility](Compatibility.md) - Which licenses can be combined
- [Standards](Standards.md) - OSI, FSF, and SPDX definitions
