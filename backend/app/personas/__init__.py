"""Persona registry — orchestrator bütün persona-ları buradan götürür."""
from .base import Persona
from .budget_applicant import persona as budget_applicant
from .career_changer import persona as career_changer
from .data_driven import persona as data_driven
from .skeptic import persona as skeptic
from .study_abroad import persona as study_abroad

# Sıra UI-da göstərilmə sırasını da müəyyən edir.
ALL_PERSONAS: list[Persona] = [
    budget_applicant,
    career_changer,
    study_abroad,
    skeptic,
    data_driven,
]

__all__ = ["Persona", "ALL_PERSONAS"]
