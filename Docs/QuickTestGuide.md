# Quick-Test Guide

LicenseWise supports a compact answer string for rapid testing, bypassing the interactive question flow.

## Usage

```bash
python -m src.main -a "ANSWER_STRING" --verbose
```

## How it works

The answer string is parsed character-by-character against the question list. Each character maps to one answer. Conditional questions (that are skipped based on earlier answers) do **not** consume a character — so the string length varies depending on your answers.

## Character mapping

| Char | `yes_no_skip` questions | `choice` questions |
|------|------------------------|-------------------|
| `y`  | Yes (True)             | —                 |
| `n`  | No (False)             | —                 |
| `s` or `.` | Skip (None)      | —                 |
| `1`  | —                      | Choice 1          |
| `2`  | —                      | Choice 2          |
| `3`  | —                      | Choice 3          |

## Recommendation mode — question order

Questions are asked in this order. Questions marked with * are conditional and may be skipped.

| #  | Fact name                      | Type        | Conditional on           |
|----|-------------------------------|-------------|--------------------------|
| 1  | `distribute`                  | yes_no_skip | —                        |
| 2  | `saas`                        | yes_no_skip | —                        |
| 3  | `commercial_use`              | yes_no_skip | —                        |
| 4  | `need_patent_protection`      | yes_no_skip | —                        |
| 5  | `want_copyleft`               | yes_no_skip | —                        |
| 6  | `want_weak_copyleft`          | yes_no_skip | * want_copyleft = true   |
| 7  | `want_file_copyleft`          | yes_no_skip | * want_copyleft = true, unless weak_copyleft = true |
| 8  | `wants_relicense`             | yes_no_skip | —                        |
| 9  | `project_type`                | choice      | —                        |
| 10 | `linking_type`                | choice      | * project_type = "library" |
| 11 | `modify_library`              | yes_no_skip | * project_type = "library" |
| 12 | `want_public_domain`          | yes_no_skip | —                        |
| 13 | `want_simple_permissive`      | yes_no_skip | * want_public_domain = false |
| 14 | `academic_project`            | yes_no_skip | —                        |
| 15 | `mixed_open_proprietary`      | yes_no_skip | —                        |
| 16 | `concerned_about_legal_recognition` | yes_no_skip | —                |

## Choice question values

| Question    | Choice `1` | Choice `2` | Choice `3` |
|------------|-----------|-----------|-----------|
| `project_type` | Software | Library | Content |
| `linking_type` | Dynamic | Static | — |

## Examples

### Simple closed-source project (12 chars)

No copyleft, no library, no public domain.

```
y n y n n n 1 n n n n n
1 2 3 4 5   8 9 .. .. ..
        (6,7 skipped)
```

```bash
python -m src.main -a "ynyynn1nnnnn" --verbose
```

Breakdown:
- `y` = distribute: yes
- `n` = saas: no
- `y` = commercial: yes
- `n` = patent: no
- `n` = copyleft: no (skips questions 6, 7)
- `n` = relicense: no
- `1` = project_type: Software (skips questions 10, 11)
- `n` = public_domain: no
- `n` = simple_permissive: no
- `n` = academic: no
- `n` = mixed: no
- `n` = jurisdictional concern: no

### Full copyleft + library (16 chars)

Copyleft, not weak, file-level, static linking, modifying library.

```
y n y n y n y n 2 2 y n n n n n
1 2 3 4 5 6 7 8 9 .. 0 1 2 3 4 5
```

```bash
python -m src.main -a "ynynynyn22ynnnnn" --verbose
```

Breakdown:
- `y` = distribute: yes
- `n` = saas: no
- `y` = commercial: yes
- `n` = patent: no
- `y` = copyleft: yes
- `n` = weak_copyleft: no
- `y` = file_copyleft: yes
- `n` = relicense: no
- `2` = project_type: Library
- `2` = linking_type: Static
- `y` = modify_library: yes
- `n` = public_domain: no
- `n` = simple_permissive: no
- `n` = academic: no
- `n` = mixed: no
- `n` = jurisdictional concern: no

### Weak copyleft + library (13 chars)

Copyleft, weak (library-level), file_copyleft skipped, non-library project.

```
y n y n y y n 1 n n n n n
1 2 3 4 5 6   8 9 .. .. ..
        (7 skipped)
```

```bash
python -m src.main -a "ynyynyn1nnnnn" --verbose
```

### Public domain (12 chars)

```bash
python -m src.main -a "ynnnnn1ynnnn" --verbose
```

Breakdown:
- `y` = distribute: yes
- `n` = saas: no
- `n` = commercial: no
- `n` = patent: no
- `n` = copyleft: no (skips questions 6, 7)
- `n` = relicense: no
- `1` = project_type: Software (skips questions 10, 11)
- `y` = public_domain: yes (skips question 13)
- `n` = academic: no
- `n` = mixed: no
- `n` = jurisdictional concern: no

## Analysis mode

Analysis mode asks 5 fixed yes_no_skip questions (no conditionals). Use a 5-character string:

```
distribute saas commercial patent relicense
  y/n/s     y/n/s  y/n/s    y/n/s   y/n/s
```

```bash
# Example: distribute, no SaaS, commercial, no patent, no relicense
python -m src.main -a "ynyyn" --verbose
```

Note: Analysis mode still prompts for the license ID interactively. Only the fact questions are bypassed.

## Tips

- If the answer string is shorter than the number of asked questions, remaining questions are skipped (treated as "skip").
- If the answer string is longer than needed, extra characters are ignored.
- Spaces in the string are ignored — you can format it however you like: `"y n y n"` or `"ynyn"` both work the same.
- Use `--verbose` to see the full reasoning trace and confirm the parser interpreted your answers correctly.
