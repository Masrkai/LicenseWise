# Compliance and Disclaimers

How to follow license requirements and legal best practices.

## Compliance Requirements

| Term | Plain Explanation | Which Licenses Require? |
|------|-------------------|-------------------------|
| **Compliance** | The act of following all the requirements of a license (e.g., including copyright notices, disclosing source code). | All licenses |
| **Include Copyright Notice** | The requirement to keep the original copyright notice intact when using or distributing the software. | All licenses with attribution |
| **Include License Text** | The requirement to include the full license text when distributing the software. | GPL, LGPL, Apache, MPL |
| **Document Changes** | The requirement to record and describe modifications made to the licensed software. | Apache-2.0, GPL, LGPL |
| **Disclose Source Code** | The requirement to make the source code available to recipients. | GPL, AGPL, LGPL |
| **Attribution** | The requirement to give credit to the original author when using, modifying, or redistributing the software. | MIT, BSD, Apache, CC licenses |

## License Violations

| Term | Plain Explanation | Consequences |
|------|-------------------|--------------|
| **Violations** | When a license's conditions are not met, constituting a breach of the license terms. | License termination, legal action |
| **License Termination** | Automatic revocation of rights if conditions are violated. Some licenses allow cure periods. | Loss of rights to use the software |
| **Cure Period** | A grace period to fix a violation before the license is terminated. | GPL-3.0, AGPL-3.0 provide 30-day cure periods |

## Compliance Checklist by License Type

### Permissive (MIT, BSD, Apache)

- [ ] Include copyright notice
- [ ] Include license text
- [ ] Document changes (Apache-2.0)
- [ ] Include patent notice (Apache-2.0)

### Weak Copyleft (LGPL, MPL, EPL)

- [ ] All permissive requirements, plus:
- [ ] Keep modified library files under same license
- [ ] Allow dynamic linking without copyleft spread
- [ ] Document changes to library files

### Strong Copyleft (GPL, AGPL)

- [ ] All permissive requirements, plus:
- [ ] Release entire derivative work under same license
- [ ] Provide source code to recipients
- [ ] Document all changes
- [ ] Include all license notices
- [ ] (AGPL) Provide source to network users

### Creative Commons

- [ ] Attribution (all CC licenses)
- [ ] Non-commercial use only (NC variants)
- [ ] Share-alike for derivatives (SA variants)
- [ ] No derivatives (ND variants, not in LicenseWise)

## Legal Disclaimers

| Term | Plain Explanation | Why It Matters |
|------|-------------------|----------------|
| **Disclaimer** | A statement that the tool's output is not legal advice and should not be relied upon for legal decisions. | Protects the tool provider from liability |
| **Not Legal Advice** | A standard legal disclaimer stating that the information provided does not constitute professional legal counsel. | Users should verify independently |
| **Consult a Lawyer** | Recommendation that users seek professional legal advice for production use. | Complex situations need expert review |

## Best Practices

1. **Always include copyright notices** - Even if not required, it's good practice
2. **Keep license texts with distributed software** - Store them alongside your code
3. **Document changes clearly** - Use version control and changelogs
4. **Track dependencies' licenses** - Use SPDX identifiers in your build system
5. **Review before distribution** - Check license compatibility before releasing
6. **Consult legal experts** - For commercial or high-risk projects

## See Also

- [Legal_Concepts](Legal_Concepts.md) - Core legal rights and protections
- [Distribution_Terms](Distribution_Terms.md) - How sharing triggers requirements
- [License_Types](License_Types.md) - All supported licenses
