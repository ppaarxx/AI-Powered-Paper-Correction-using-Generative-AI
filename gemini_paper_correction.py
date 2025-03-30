import pdfplumber
from fpdf import FPDF
import requests
import json

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = ""
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    return extracted_text

def generate_prompt(student_text, teacher_text):
    return (
        f"Evaluate the student's answers compared to the correct answers provided by the teacher.\n\n"
        f"Please evaluate the student's responses for correctness, clarity, and relevance. "
        f"Provide a very short feedback, including suggestions for improvement. "
        f"Also, assign marks to the student on a scale of 0 to 100."
        f"Dont Give any corrections give just the marks and feedback."
        f"Teacher's Answer Sheet:\n{teacher_text}\n\n"
        f"Student's Answer Sheet:\n{student_text}\n\n"
    )

def evaluate_responses_with_gemini(teacher_text, student_text, api_key):
    prompt = generate_prompt(student_text, teacher_text)
    url = f" "
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        final_feedback = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No feedback available.")
        return final_feedback
    else:
        raise Exception(f"Error from Gemini API: {response.text}")

def generate_feedback_pdf(feedback_text, output_pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Student Evaluation and Feedback", ln=True, align="C")
    pdf.ln(10)
    pdf.multi_cell(0, 10, feedback_text)
    pdf.output(output_pdf_path)
    print(f"Feedback PDF saved as {output_pdf_path}")

# Function Calls
# Student Extraction
student_pdf = "Student_Answer_Sheet\Student_Answer_Sheet.pdf"
student_text = extract_text_from_pdf(student_pdf)
# Teacher Extraction
teacher_pdf = "Teacher_Answer_Sheet\Answer_only.pdf"
teacher_text = extract_text_from_pdf(teacher_pdf)
# Final Results
output_feedback_pdf_path = "Student_Feedback.pdf"
api_key = " "
feedback_text = evaluate_responses_with_gemini(teacher_text, student_text, api_key)
generate_feedback_pdf(feedback_text, output_feedback_pdf_path)