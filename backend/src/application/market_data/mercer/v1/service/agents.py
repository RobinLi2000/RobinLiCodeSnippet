import ast
import difflib
import json
import logging
import re

from ......infrastructure.service.llm.model import (
    AzureOpenAIGPT4O,
    AzureOpenAIGPT35Turbo,
)

logger = logging.getLogger(__name__)


def string_to_list(input_string: str):
    """
    Converts a string representation of a list to an actual list if it contains a valid list pattern.

    Args:
        input_string (str): The string to be converted.

    Returns:
        list or str: The converted list or an error message.
    """
    # Use regex to check for a valid list pattern
    if re.search(r"\[.*\]", input_string):
        try:
            # Extract the first occurrence of a list pattern
            match = re.search(r"\[.*?\]", input_string)
            list_str = match.group(0)  # Get the matched list pattern

            # Attempt to evaluate the string as a Python literal
            result = ast.literal_eval(list_str)

            # Check if the result is a list
            if isinstance(result, list):
                return result
            else:
                return "Error: The string does not represent a list."
        except (ValueError, SyntaxError) as e:
            return f"Error: {e}"
    else:
        return "Error: No list pattern found in the string."


async def level_determine_agent(level_info):
    llm = AzureOpenAIGPT35Turbo()
    prompt = """
    You are a inhouse HR consultant. Your job is to fit the group's internal level info into market criteria. Your output should be in list of string format.
    If the groups's level is Grade 7, the desired output is ["M1", "P3", "P2", "S3", "S2"] 
    If the group's level is Grade 3, desired output should be ["M4"]
    Do not output any other content, just the result list.
    """
    streamer = await llm(
        prompt=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": level_info},
        ],
        stream=False,
    )
    return streamer


def level_determine(internal_level):
    match internal_level:
        case "Grade 7" | "grade 7":
            result = ["M1", "P3", "P2", "S3", "S2"]
        case "CEO":
            result = ["E3"]
        case "GM" | "BL":
            result = ["E2"]
        case "Function Head" | "Director":
            result = ["E1"]
        case "Grade 3" | "grade 3":
            result = ["M4"]
        case "Grade 4" | "grade 4":
            result = ["M3"]
        case "Grade 5" | "grade 5":
            result = ["M2", "P3"]
        case "Grade 6" | "grade 6":
            result = ["M2", "P3"]
        case "Grade 8" | "grade 8":
            result = ["P1", "S3", "S2", "S1"]
        case "Grade 9" | "grade 9":
            result = ["S1"]
        case _:
            result = ["M1", "P3", "P2", "S3", "S2", "E3"]
    return result


def parse_valid_string(input_str: str, template: dict):
    try:
        # Parse the input string as JSON
        data = json.loads(input_str)
    except json.JSONDecodeError:
        # If parsing fails, the string is not valid JSON
        return None

    def validate(data, template):
        for key, value_type in template.items():
            if key not in data:
                return None
            # Check if the value is of the correct type
            if isinstance(value_type, dict):
                if not isinstance(data[key], dict):
                    return None
                if validate(data[key], value_type) is None:
                    return None
            elif isinstance(value_type, list) and len(value_type) > 0:
                element_type = value_type[0]
                if not isinstance(data[key], list) or not all(
                    isinstance(item, element_type) for item in data[key]
                ):
                    return None
            elif not isinstance(data[key], value_type):
                return None
        return data

    return validate(data, template)


async def subfamily_determine_agent(title, JD, topk: int = 5):
    llm = AzureOpenAIGPT4O()
    subfamilies = [
        "General Management",
        "Business Strategy & Planning",
        "Risk Management",
        "Finance & Accounting Leadership",
        "Finance Generalists",
        "Financial Control",
        "Management Accounting",
        "Accounting",
        "Tax",
        "Treasury",
        "Accounts Payable/Receivable",
        "Credit & Collections",
        "Human Resources Leadership",
        "Human Resources Generalists",
        "Mobility",
        "Compensation & Benefits",
        "Human Resources Operations",
        "Payroll",
        "Employee/Labor Relations & Diversity",
        "Talent Acquisition",
        "Talent Management & Organization Development",
        "Training & Development (Internal)",
        "Communications & Corporate Affairs Leadership",
        "Communications & Corporate Affairs Generalists",
        "Employee Communications & Collaboration",
        "Corporate Affairs",
        "Investor Relations",
        "Corporate Compliance & Legal Leadership",
        "Legal & Compliance Management",
        "Legal",
        "Regulatory Affairs",
        "Internal Audit",
        "Fraud Management",
        "Compliance",
        "Environmental and Employee Health & Safety",
        "Administration & Secretarial",
        "Facilities Management & Planning",
        "Facilities Refurbishment, Repair & Maintenance",
        "Facilities/Grounds, Custodial, Cleaning & Laundry",
        "Property, Facilities & Asset Security",
        "Library Services",
        "Safety Services",
        "General Business Project/Program Management",
        "Technical Project/Program Management",
        "Sales, Marketing & Product Management Leadership",
        "Sales & Marketing",
        "Marketing Generalists",
        "Product Marketing & Management",
        "Advertising & Marketing Communications",
        "Market Research & Analysis",
        "Field Sales & Account Management",
        "Remote/Telesales & Account Management",
        "Account & Client Management",
        "Sales Training",
        "Sales Operations/Administration",
        "Customer Service & Contact Center Operations Leadership",
        "Customer Service",
        "Customer Relationship Management, Issue Resolution & Account Activation",
        "Contact Center Operations & Training",
        "Quality Management Leadership",
        "Business Process/Service Quality",
        "Manufacturing/Product Quality",
        "Supplier Quality",
        "General Business Quality Management",
        "Supply Chain Leadership",
        "Supply Chain Planning & Operations",
        "Procurement",
        "Logistics",
        "Warehousing & Distribution",
        "Import/Export & Customs Operations",
        "Joint Engineering & Science Technical Leadership",
        "Technical Product Development/Research Operations",
        "Engineering",
        "Engineering Technologists & Technicians",
        "Engineering Design Services",
        "Science",
        "Science Technical Research",
        "Science Research & Quality Laboratory Services",
        "Manufacturing Plant Management",
        "Manufacturing Production, Processing & Assembly",
        "Production Planning & Control",
        "Machine Operations",
        "Repair & Maintenance Trades",
        "Heavy Equipment & Construction Trades",
        "Agricultural/Farming Production Operations",
        "Food & Beverage Processing",
        "IT, Telecom & Internet Leadership",
        "IT, Telecom & Internet Generalists",
        "Information Systems Architecture",
        "IT Business Systems Analysts",
        "IT Systems Configuration & Programming",
        "IT Applications Development",
        "IT Security",
        "IT Infrastructure & Systems Administration",
        "Information Systems Administration & Reporting",
        "IT User Support",
        "Information Systems Operations & Production Control",
        "Data Analytics/Warehousing, & Business Intelligence Management",
        "Data Analytics & Business Intelligence (BI)",
        "Internal Data Engineering & Warehousing",
        "Back-End Transaction/Data Processing",
        "General Transportation Services",
        "Road Transportation",
        "Air Transportation",
        "Restaurant & Hotel/Resort Operations",
        "Non-Restaurant Food Service Provider Operations",
        "Food & Beverage Preparation/Table Service",
        "Food Planning & Development",
        "Product Creative/Industrial Design",
        "Media/Communications Creative & Design",
        "Web/New Media Creative & User Interface Design",
        "Advertising Creative, Design & Production",
        "Architecture & Interior/Landscape Design",
        "General Real Estate Management",
        "Real Estate Acquisition, Planning & Development",
        "Construction Leadership",
        "Physician Services",
        "Nursing Services",
        "Behavioral Health/Social Services",
        "Personal Care Services",
    ]

    subfamilies_string = "\n".join(subfamilies)

    # prompt = f"""
    # You are a inhouse HR recruiter. Your job is to fit the group's job position into market criteria. Here is a list of all fields:
    # {subfamilies_string}
    # =================================
    # You should determine which fields this job position is most likely to fit into. Your output should be in list of string format with {str(topk)} fields you feel the most likely to fit into. No other content is needed. Just a list showing your result.
    # Please keep the filed names unchanged.
    # There are some fields whose meaning is very similar, when you meet some complex case, the best practice is including all the similar fields in your answer.
    # You are asked to output in list of string format. Sample output: ["Tax", "Market Research & Analysis"]
    # """

    new_prompt = f"""
    You are an inhouse HR recruiter. Your job is to fit the group's job position into market criteria. Here is a list of all fields:
    {subfamilies_string}
    =================================
    Title: {title}
    Job Description: {JD}
    
    Extract and output two lists of matching fields:
    1. Based on title analysis: Extract fields that match with the job title's function, level, and domain
    2. Based on JD analysis: Extract fields that match with the job description's responsibilities, skills, and requirements
    
    Your output should be in JSON format with {str(topk)} fields in each list.
    Please keep the field names unchanged.
    There are some fields whose meaning is very similar, when you meet some complex case, the best practice is including all the similar fields in your answer.
    You are asked to output in JSON format.
    Please do not output any other content. If you can't find any matching fields, just output an empty list within the format template.
    
    Output format:
    {{
        "title_subfamilies": ["field1", "field2", ...],
        "jd_subfamilies": ["field1", "field2", ...]
    }}
    """
    template = {"title_subfamilies": [str], "jd_subfamilies": [str]}
    response: str = await llm(
        prompt=[{"role": "system", "content": new_prompt}],
        stream=False,
    )

    result_dict = parse_valid_string(response, template)

    if result_dict is None:
        return {"title_subfamilies": [], "jd_subfamilies": []}

    # result_dict = json.loads(result_json)

    # results = string_to_list(result_string)

    # if type(results) is not list or len(results) == 0:
    #     return []
    final_results = {"title_subfamilies": [], "jd_subfamilies": []}
    for k, results in result_dict.items():
        for i, result in enumerate(results):
            if result in subfamilies:
                final_results[k].append(result)
                continue

        matches = difflib.get_close_matches(result, subfamilies)
        if len(matches) > 0:
            final_results[k].append(matches[0])

    return final_results


async def keyword_extraction_agent(JD, title):
    llm = AzureOpenAIGPT4O()

    # prompt = """
    # Please extract the most relevant keywords from the user provided job description. Focus on identifying key skills, qualifications, responsibilities, and any specific industry terms mentioned. The goal is to highlight the essential elements that define the role and its requirements.
    # You can also generate some relevant keywords based on your own knowledge.
    # Your output should be in the format of a list of string (keywords). No other content is needed. Just a list showing your result.
    # Please generate as many as keywords you can, don't afraid of meaning overlapping.
    # The keywords should focus on functionalities, skills, qualifications, responsibilities, and any specific industry terms mentioned. Do not include specific address, visa information, working hours, and other likelihood keywords etc.
    # You are asked to output in list of string format. Output example: ["financial management", "leadership", "revenue management"]
    # Please strictly follow the output format!!!!
    # """
    new_prompt = f"""
    JD: {JD}
    Title: {title}
    Please extract relevant keywords separately from both the title and job description.

    For JD keywords (up to 30):
    1. Technical skills and competencies
    2. Required qualifications and certifications
    3. Core job responsibilities
    4. Industry-specific terminology
    5. Tools and technologies
    6. Required soft skills
    7. Domain knowledge requirements

    For title keywords (up to 10):
    1. Role/position level
    2. Technical domain
    3. Function area
    4. Industry-specific terms

    Guidelines:
    - Generate only the most essential and relevant keywords
    - Include both explicitly mentioned terms and strongly implied skills
    - Avoid generic terms, locations, visa requirements, or administrative details
    - Each keyword should be lowercase and use minimal words

    Output format:
    {{
        "title_keywords": ["keyword1", "keyword2", ...],
        "jd_keywords": ["keyword1", "keyword2", ...]
    }}

    Note: The output must be exactly in JSON format with two arrays of strings, with keywords in quotes and separated by commas.
    """
    template = {"title_keywords": [str], "jd_keywords": [str]}
    response: str = await llm(
        prompt=[{"role": "system", "content": new_prompt}],
        stream=False,
    )

    result_dict = parse_valid_string(response, template)

    if result_dict is None:
        return {"title_keywords": [], "jd_keywords": []}
    logging.info(f"result_dict_keyword: {result_dict}")
    return result_dict


async def es_query_agent(JD):
    llm = AzureOpenAIGPT4O()

    prompt = """
    Please extract the most relevant keywords from the user provided job description. Focus on identifying key skills, qualifications, responsibilities, and any specific industry terms mentioned. The goal is to highlight the essential elements that define the role and its requirements.
    You can also generate some relevant keywords based on your own knowledge.
    Your output should be in the format of a list of string (keywords). No other content is needed. Just a list showing your result.
    Please generate as many as keywords you can, don't afraid of meaning overlapping.
    The keywords should focus on functionalities, skills, qualifications, responsibilities, and any specific industry terms mentioned. Do not include specific address, visa information, working hours, and other likelihood keywords etc.
    You are asked to output in list of string format. Output example: ["financial management", "leadership", "revenue management"]. Please strictly follow the output format!!!!
    """
    streamer = await llm(
        prompt=[{"role": "system", "content": prompt}, {"role": "user", "content": JD}],
        stream=False,
    )
    return streamer
