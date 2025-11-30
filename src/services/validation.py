"""Fiscal data validation helpers."""


def validate_nb_parts(
    situation_familiale: str,
    nb_parts: float,
    enfants_a_charge: int = 0,
) -> list[str]:
    """
    Validate nombre_parts against situation familiale.

    Checks if the declared nombre de parts fiscales is coherent with
    the family situation (marital status + children).

    French fiscal rules:
    - Célibataire, divorcé(e), veuf(ve): 1.0 base part
    - Marié(e), pacsé(e): 2.0 base parts
    - First 2 children: +0.5 parts each
    - 3rd child and beyond: +1.0 part each

    Args:
        situation_familiale: Family situation
            (celibataire, marie, pacse, divorce, veuf)
        nb_parts: Declared nombre de parts fiscales
        enfants_a_charge: Number of dependent children

    Returns:
        List of warning messages (empty if valid)

    Example:
        >>> warnings = validate_nb_parts("celibataire", 1.0, 0)
        >>> warnings  # []
        >>> warnings = validate_nb_parts("marie", 1.0, 0)
        >>> warnings  # ["Incohérence détectée: ..."]
    """
    warnings = []

    # Normalize situation_familiale
    situation = situation_familiale.lower().strip()

    # Calculate expected base parts
    if situation in ["celibataire", "divorce", "divorcé", "divorcée", "veuf", "veuve"]:
        expected_base = 1.0
    elif situation in ["marie", "marié", "mariée", "pacse", "pacsé", "pacsée"]:
        expected_base = 2.0
    else:
        # Unknown situation, skip validation
        return warnings

    # Add children parts
    # French fiscal rule: +0.5 for 1st and 2nd child, +1.0 from 3rd onward
    expected_total = expected_base
    for i in range(enfants_a_charge):
        if i < 2:
            expected_total += 0.5
        else:
            expected_total += 1.0

    # Check coherence (allow 0.5 tolerance for edge cases)
    if abs(nb_parts - expected_total) > 0.5:
        warnings.append(
            f"Incohérence détectée : situation '{situation_familiale}' "
            f"avec {enfants_a_charge} enfant(s) devrait avoir "
            f"environ {expected_total} part(s) fiscale(s), "
            f"mais {nb_parts} part(s) déclarée(s)."
        )

    return warnings


def validate_fiscal_profile_coherence(
    profil: dict,
) -> list[str]:
    """
    Validate overall fiscal profile coherence.

    Runs multiple validation checks on the fiscal profile data
    and returns aggregated warnings.

    Args:
        profil: Fiscal profile dict with:
            - situation_familiale: str
            - nombre_parts: float
            - enfants_a_charge: int
            - chiffre_affaires: float (optional)
            - cotisations_sociales: float (optional)

    Returns:
        List of warning messages

    Example:
        >>> warnings = validate_fiscal_profile_coherence({
        ...     "situation_familiale": "marie",
        ...     "nombre_parts": 2.0,
        ...     "enfants_a_charge": 0
        ... })
        >>> warnings  # []
    """
    all_warnings = []

    # Validation 1: nb_parts vs situation_familiale
    if all(k in profil for k in ["situation_familiale", "nombre_parts"]):
        warnings = validate_nb_parts(
            situation_familiale=profil["situation_familiale"],
            nb_parts=profil["nombre_parts"],
            enfants_a_charge=profil.get("enfants_a_charge", 0),
        )
        all_warnings.extend(warnings)

    # Validation 2: CA vs cotisations sociales (optional - can be added later)
    # Example: if CA > 0 but cotisations = 0, warn about missing URSSAF
    chiffre_affaires = profil.get("chiffre_affaires", 0.0)
    cotisations_sociales = profil.get("cotisations_sociales", 0.0)

    if chiffre_affaires > 10000 and cotisations_sociales == 0:
        all_warnings.append(
            f"Attention : Chiffre d'affaires de {chiffre_affaires:.2f}€ "
            "mais aucune cotisation sociale déclarée. "
            "Vérifiez vos cotisations URSSAF."
        )

    return all_warnings
