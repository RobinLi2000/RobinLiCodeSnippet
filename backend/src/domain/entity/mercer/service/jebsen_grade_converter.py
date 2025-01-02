from ....common.enums.company_grade import CompanyGrade
from ..enums.mercer_grade import MercerGrade


def convert_grade_from_jebsen_to_mercer(grade: CompanyGrade) -> list[MercerGrade]:
    match grade.value:
        case "Grade 7" | "grade 7":
            return [
                MercerGrade.M1,
                MercerGrade.P3,
                MercerGrade.P2,
                MercerGrade.S3,
                MercerGrade.S2,
            ]
        case "CEO":
            return [MercerGrade.E3]
        case "GM":
            return [MercerGrade.E2]
        case "Function Head" | "Director":
            return [MercerGrade.E1]
        case "Grade 3" | "grade 3":
            return [MercerGrade.M4]
        case "Grade 4" | "grade 4":
            return [MercerGrade.M3]
        case "Grade 5" | "grade 5":
            return [MercerGrade.M2, MercerGrade.P3]
        case "Grade 6" | "grade 6":
            return [MercerGrade.M2, MercerGrade.P3]
        case "Grade 8" | "grade 8":
            return [MercerGrade.P1, MercerGrade.S3, MercerGrade.S2, MercerGrade.S1]
        case "Grade 9" | "grade 9":
            return [MercerGrade.S1]
        case _:
            return [
                MercerGrade.M1,
                MercerGrade.P3,
                MercerGrade.P2,
                MercerGrade.S3,
                MercerGrade.S2,
                MercerGrade.E3,
            ]
