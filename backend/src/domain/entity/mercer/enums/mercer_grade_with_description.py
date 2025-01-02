from enum import Enum


class MercerGradeWithDescription(str, Enum):
    E3 = "E3 Org Head/Function Head/Sub-Function Head"
    E2 = "E2 Org Head/Function Head/Sub-Function Head"
    E1 = "E1 Function Head/Sub-Function Head"
    M4 = "M4 Senior Manager"
    M3 = "M3 Manager"
    M2 = "M2 Team Leader (Professionals)"
    M1 = "M1 Team Leader (Para-Professionals)"
    P6 = "P6 Pre-eminent Professional"
    P5 = "P5 Expert Professional"
    P4 = "P4 Specialist Professional"
    P3 = "P3 Senior Professional"
    P2 = "P2 Experienced Professional"
    P1 = "P1 Entry Professional"
    S4 = "S4 Specialist Para-Professional"
    S3 = "S3 Senior Para-Professional"
    S2 = "S2 Experienced Para-Professional"
    S1 = "S1 Entry Para-Professional"
