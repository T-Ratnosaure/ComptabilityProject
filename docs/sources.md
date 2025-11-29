# Sources Officielles - Phase 3: Tax Calculation Engine

This document lists all official sources used for the French tax calculation implementation.

## Impôt sur le Revenu (IR)

### Official Government Sources

1. **Calcul de l'impôt sur le revenu**
   - URL: https://www.impots.gouv.fr/particulier/calcul-de-limpot
   - Description: Official tax calculation methodology from Direction Générale des Finances Publiques (DGFiP)
   - Used for: Progressive tax brackets (barèmes), quotient familial rules

2. **Barème progressif 2024**
   - URL: https://www.service-public.fr/particuliers/vosdroits/F1419
   - Description: Official 2024 income tax brackets and rates
   - Used for: Validation of tranches (0%, 11%, 30%, 41%, 45%)

3. **Quotient familial**
   - URL: https://www.impots.gouv.fr/particulier/questions/quest-ce-que-le-quotient-familial
   - Description: Family quotient calculation rules
   - Used for: nb_parts calculation, plafonnement rules

## Régimes Micro-Entrepreneurs

### BNC (Bénéfices Non Commerciaux)

1. **Régime micro-BNC**
   - URL: https://www.impots.gouv.fr/particulier/questions/je-suis-en-regime-micro-bnc-comment-sont-imposes-mes-revenus
   - Description: Micro-BNC taxation rules and abattement forfaitaire
   - Used for: 34% abattement rate, threshold of 77,700€

### BIC (Bénéfices Industriels et Commerciaux)

2. **Régime micro-BIC**
   - URL: https://www.impots.gouv.fr/particulier/questions/je-suis-en-regime-micro-bic-comment-sont-imposes-mes-revenus
   - Description: Micro-BIC taxation rules for services and sales
   - Used for:
     - Prestations de services: 50% abattement, threshold 77,700€
     - Ventes de marchandises: 71% abattement, threshold 188,700€

## Cotisations Sociales (URSSAF)

### Auto-Entrepreneur Rates

1. **Taux de cotisations sociales 2024**
   - URL: https://www.urssaf.fr/portail/home/independant/je-suis-auto-entrepreneur/lessentiel-du-statut.html
   - Description: Official URSSAF contribution rates for auto-entrepreneurs
   - Used for:
     - Professions libérales (BNC): 21.8%
     - Activités commerciales (BIC): 12.8%

2. **Simulateur URSSAF**
   - URL: https://www.autoentrepreneur.urssaf.fr/portail/accueil/simulateur-de-cotisations.html
   - Description: Official URSSAF calculator for validation
   - Used for: Test case validation

## Plan d'Épargne Retraite (PER)

1. **Plafonds de déduction PER 2024**
   - URL: https://www.service-public.fr/particuliers/vosdroits/F34982
   - Description: PER contribution deduction limits
   - Used for: PER plafond calculation (10% of professional income, min €4,399, max €35,194)

2. **PER et déduction fiscale**
   - URL: https://www.impots.gouv.fr/particulier/questions/puis-je-deduire-mes-cotisations-versees-sur-un-per
   - Description: PER deduction rules for income tax
   - Used for: Deduction logic in revenu imposable calculation

## Prélèvement à la Source (PAS)

1. **Le prélèvement à la source**
   - URL: https://www.impots.gouv.fr/particulier/le-prelevement-la-source
   - Description: Withholding tax system overview
   - Used for: PAS reconciliation logic

2. **Taux de PAS pour indépendants**
   - URL: https://www.impots.gouv.fr/particulier/questions/comment-est-calcule-mon-taux-de-prelevement-la-source
   - Description: PAS rate calculation for self-employed
   - Used for: Understanding PAS vs final tax settlement

## Legal Framework

### Code Général des Impôts (CGI)

1. **Article 50-0 (Micro-BIC)**
   - Reference: CGI, Article 50-0
   - Description: Legal basis for micro-BIC regime
   - Used for: Threshold verification and regime applicability

2. **Article 102 ter (Micro-BNC)**
   - Reference: CGI, Article 102 ter
   - Description: Legal basis for micro-BNC regime
   - Used for: Threshold verification and abattement rules

3. **Article 197 (Barème progressif)**
   - Reference: CGI, Article 197
   - Description: Progressive income tax brackets
   - Used for: Tax calculation methodology

## Validation Sources

### Test Case Validation

1. **Simulateur impots.gouv.fr**
   - URL: https://www.impots.gouv.fr/simulateurs
   - Description: Official tax simulator for validation
   - Used for: Validating test case results (Cas A, Cas B)

2. **Simulateur URSSAF auto-entrepreneur**
   - URL: https://mon-entreprise.urssaf.fr/simulateurs/auto-entrepreneur
   - Description: Official URSSAF simulator
   - Used for: Validating social contribution calculations

## Data Sources in Code

### Barèmes JSON Files

- **baremes_2024.json**: Contains all official 2024 tax rules
  - Income tax brackets (verified against impots.gouv.fr)
  - Abattements (verified against CGI and service-public.fr)
  - URSSAF rates (verified against urssaf.fr)
  - PER plafonds (verified against service-public.fr)
  - Micro thresholds (verified against impots.gouv.fr)

- **baremes_2025.json**: Contains estimated 2025 tax rules
  - Note: 2025 rules are preliminary estimates pending official publication
  - Will be updated when official 2025 barème is published (typically in December 2024)

## Disclaimer

**IMPORTANT**: This implementation is for estimation purposes only and does not replace professional tax advice. French tax law is complex and individual situations may require expert consultation:

- Always validate results with official simulators
- Consult a certified expert-comptable for complex cases
- Verify current year rules on official government websites
- Tax rules may change; ensure barèmes are up to date

## Update Schedule

Tax rules should be reviewed and updated:
- **Annually**: When new tax brackets are published (typically December)
- **As needed**: When URSSAF rates change
- **Before production**: Validate all rates against current official sources

## Contact for Official Information

- **DGFiP (Tax Administration)**: https://www.impots.gouv.fr/contact
- **URSSAF**: https://www.urssaf.fr/portail/home/contacts.html
- **Service-Public.fr**: https://www.service-public.fr/

---

**Last Updated**: 2025-11-26
**Barèmes Version**: 2024 (validated), 2025 (preliminary)
**Maintainer**: ComptabilityProject Team
