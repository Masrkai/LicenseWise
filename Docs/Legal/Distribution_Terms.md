# Distribution Terms

How software is shared and what conditions apply when you give it to others.

## Core Distribution Concepts

| Term | Plain Explanation | Triggers License Conditions? |
|------|-------------------|------------------------------|
| **Distribution** | Giving copies of the software to other people or organizations. This is the trigger for many license conditions (copyleft, attribution, etc.). | Yes - this is the main trigger |
| **Private Use** | Using the software privately without distributing it to others. Most licenses allow this without conditions. | No |
| **Source Disclosure** | The requirement to make the source code available to recipients. Strong copyleft licenses (GPL, AGPL) require this; permissive licenses do not. | Only for strong copyleft |
| **Disclose Source Code** | Same as source disclosure -- the license condition requiring you to share your source code when distributing the software. | Only for strong copyleft |

## Distribution Methods

| Term | Plain Explanation | License Implications |
|------|-------------------|---------------------|
| **Binary Distribution** | Distributing the software in compiled/executable form (not source code). Some licenses have different requirements for binary vs. source distribution. | May trigger attribution, license text inclusion |
| **Source Distribution** | Distributing the software as readable source code. May satisfy source disclosure requirements. | Satisfies most copyleft requirements |
| **SaaS** (Software as a Service) | Running the software as a web service where users access it over a network. Traditional copyleft does not trigger because no "distribution" occurs. | Only AGPL triggers copyleft here |
| **Managed Service** | Offering the software as a hosted service to customers. The Elastic License prohibits this. | Restricted by Elastic-2.0 |

## Derivative Works

| Term | Plain Explanation | License Implications |
|------|-------------------|---------------------|
| **Derivative Works** | Any work based on or derived from the original software. Under copyright law, creating a derivative work requires permission from the copyright holder. | Copyleft requires same license |
| **Same License** | The requirement that derivative works must be released under the same license as the original. This is the core mechanism of copyleft. | Core of copyleft |
| **Modifications** | Changes made to the original software. Licenses specify whether modifications are allowed and what conditions apply to them. | Must follow license terms |

## Usage Restrictions

| Term | Plain Explanation | Which Licenses Restrict? |
|------|-------------------|-------------------------|
| **Commercial Use** | Using the software to make money or in a commercial product. Some licenses prohibit this. | CC-BY-NC, CC-BY-NC-SA |
| **Non-Commercial** | Restricting use to non-commercial purposes only. The "NonCommercial" component of CC-BY-NC licenses. | CC-BY-NC, CC-BY-NC-SA |
| **Sublicensing** | Granting a license to someone else. MIT and similar licenses allow sublicensing. | Most permissive licenses allow |

## Time-Based Terms

| Term | Plain Explanation | Which Licenses Use? |
|------|-------------------|---------------------|
| **Change Date** | A future date after which a source-available license (like BSL) converts to an open-source license, allowing unrestricted use. | BSL-1.0 |

## See Also

- [License_Classification](License_Classification.md) - How distribution triggers different copyleft types
- [Linking_Terms](Linking_Terms.md) - How software integration affects distribution
- [Compliance](Compliance.md) - How to meet distribution requirements
