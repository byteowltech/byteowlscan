
def generatePreProcessPrompt(extracted_text):
    prompt = f"""
    Preprocess the extracted text from a resume to make it clear and structured without losing any content. Follow these instructions:

    1. Preserve every piece of information exactly as it appears.
    2. Merge sentences that are split by unnecessary line breaks, but maintain breaks between meaningful sections.
    3. Remove redundant spaces and ensure proper punctuation, spacing, and capitalization.
    4. Fix minor formatting issues like missing punctuation or capitalization errors.
    5. Exclude non-content elements such as headers, footers, page numbers, or any irrelevant data.
    6. Do not modify or rephrase the content in any way.
    7. Ensure the text is well-organized and readable while retaining all original details and content structure.

    Here is the extracted text to preprocess:
    \"\"\"{extracted_text}\"\"\"
    """
    
    return prompt

def generateExtractInfo(text_chunk):
    prompt = """
    You are tasked with **extracting all information** from the following resume text into a JSON format, **ensuring that every detail is preserved exactly as it appears in the original text. Your extraction should be comprehensive and include all sections and details without any omissions or alterations.**

    **Instructions:**

    - **Language Note:** The resume text is in Vietnamese. Do not translate or alter any content. Extract the information exactly as it appears, preserving all formatting, bullet points, and line breaks within the JSON values where applicable.
    
    - **Output Format:** Organize the extracted data into a JSON object with the following structure:

    - **candidateInformation:**
        - **fullName:** Extract the full name exactly as it appears.
        - **gender:** Include the gender if mentioned.
        - **IDNo:** Include the identification number if mentioned.
        - **currentPosition:** Include the current job title or desired position.
        - **dateOfBirth:** Extract the date of birth.
        - **hometown:** Include the hometown if mentioned.
        - **phone:** Include all phone numbers.
        - **email:** Include all email addresses.
        - **address:** Extract the full address.
        - **introduce:** Extract introduce/description about profile in resume. 

    - **education:** A list of educational qualifications, each containing:
        - **degree:** The degree obtained (e.g., "Cử nhân", "Thạc sĩ", "Tiến sĩ").
        - **major:** The field of study or major.
        - **university:** The name of the university or institution.
        - **graduationDate:** The date of graduation.

    - **trainingCourses:** A list of training courses or certifications, each containing:
        - **course:** The name of the course or certification.
        - **institution:** The institution or organization providing the course.

    - **languageSkills:** Include any language skills mentioned.

    - **computerSkills:** Include any computer or technical skills mentioned.

    - **skills:** Include all other skills mentioned, both technical and soft skills.
    
    - **workExperience:** A list of work experiences, each containing:
        - **company:** The name of the company.
        - **role:** The position held.
        - **scale:** The scale or size of the company (e.g., "Quy mô 2.000 NV").
        - **duration:** The time period worked (e.g., "2018 - Hiện tại").
        - **salary:** Include the salary information for this position, if mentioned.
        - **reasonForLeaving:** Include the reason for leaving this position, if mentioned.
        - **responsibilities:** A list of all responsibilities, actions, and sentences within the work experience, **including any sub-titles or enumerated sections** (e.g., "1/ Social Media – Digital Marketing", "2/ Trưởng nhóm truyền thông (Fresher)"). Preserve numbering, bullet points, and formatting exactly as in the original text.

    - **salary:** Include any current salary information provided (if applicable and distinct from work experience salaries).

    - **references:** List any references provided, each containing relevant details.

    - **availability:** Include any information about the candidate's availability.

    - **expectedSalary:** Include any information about the candidate's expected salary.

    - **reasonForApplication:** Include the candidate's reasons for applying, as a list of strings.

    - **careerPlan:** Include any statements about the candidate's career plans.

    - **familyInformation:** Include any family information provided, as a list of objects containing relevant details.

    - **commitmentStatement:** Include any commitment statements made by the candidate.

    - **signDate:** Include the date the resume or application was signed, if available.

    - **technicalSkills:** List any technical skills mentioned.

    - **achievementsAndAwards:** List all achievements and awards.

    - **projects:** Include any projects the candidate has worked on, as a list of objects containing relevant details.

    - **volunteerExperience:** Include any volunteer experience, as a list of objects containing relevant details.

    - **additionalInformation:** Include any additional information that does not fit into the above categories.

    - **otherContent:** Include any other information that doesn't fit into the schema here.

    **Guidelines:**

    - **No Content Modification:** **Do not merge, omit, or rephrase any content.** Every piece of information should be included **exactly as it appears**.

    - **Values, Not Property Names:** **All extracted information should be treated as values within the JSON structure, not as property names derived from the resume content.** Use only the specified property names.
    
    - **No Skip Any List, Title, Subtitle in Content of Candidate Resume:** **Do not remove any content such as lists, headings, titles, or subtitles.** Ensure that all content, including nested lists and sub-sections, is captured within the appropriate JSON fields.
    
    - **Preserve Formatting:** Maintain the integrity of the original text, including any formatting such as bullet points, numbered lists, line breaks, and capitalization, within the JSON values.
    
    - **Include All Details:** Ensure that even minor or repetitive details are captured accurately. **Do not condense or summarize** any information.
    
    - **Deep Object Structure:** Use nested JSON objects to represent the hierarchical structure of the information.
    
    - **Comprehensive Extraction:** If any information seems out of place or does not fit into the specified fields, include it in the **additionalInformation** or **otherContent** field.
    
    - **Handle Sub-Sections:** Specifically, within sections like **workExperience**, ensure that any sub-sections or enumerated titles (e.g., "1/ Social Media – Digital Marketing") are included within the **responsibilities** field, preserving their numbering and formatting.
    
    - **Exclude Empty Fields:** **Only include fields in the JSON output that have corresponding data in the resume.** If a field has no data, do not include it in the JSON output.

    **Desired Output:** JSON Format

    **Provide the extracted data in the following JSON structure:**
    ```json
    {
        "candidateInformation": {
            "fullName": "",
            "gender": "",
            "IDNo": "",
            "currentPosition": "",
            "dateOfBirth": "",
            "hometown": "",
            "phone": "",
            "email": "",
            "address": "",
            "introduce": ""
        },
        "education": [
            // Include all educational qualifications
        ],
        "trainingCourses": [
            // Include all training courses
        ],
        "languageSkills": [
            // Include any language skills mentioned
        ],
        "computerSkills": [
            // Include any computer or technical skills mentioned
        ],
        "skills": {
            "technicalSkills": [
                // Include all technical skills
            ],
            "softSkills": [
                // Include all soft skills
            ]
        },
        "workExperience": [
            {
                "company": "",
                "role": "",
                "scale": "",
                "duration": "",
                "salary": "",
                "reasonForLeaving": "",
                "responsibilities": [
                    // Include all responsibilities, including sub-titles and enumerated sections
                ]
                //Another property with value related to work experience
            }
            // Include all work experiences
        ],
        "salary": "",
        "references": [
            // Include any references provided
        ],
        "availability": "",
        "expectedSalary": "",
        "reasonForApplication": [
            // Include reasons for applying
        ],
        "careerPlan": "",
        "familyInformation": [
            // Include any family information provided
        ],
        "commitmentStatement": "",
        "signDate": "",
        "achievementsAndAwards": [
            // Include all achievements and awards
        ],
        "projects": [
            // Include any projects the candidate has worked on
        ],
        "volunteerExperience": [
            // Include any volunteer experience
        ],
        "additionalInformation": {
            // Include any additional information
        },
        "otherContent": {
            // Include any other information that doesn't fit into the schema
        }
    }
    **Candidate's CV:**
    """ + text_chunk + """
    """
    
    return prompt
