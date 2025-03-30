
import pdfplumber
from fpdf import FPDF
import requests
import json
import ollama

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


def evaluate_responses_with_gemini(teacher_text, student_text):
    model = "llama3.2:3b"
    prompt = generate_prompt(student_text, teacher_text)

    response = ollama.generate(
            model=model,
            prompt=prompt, 
            stream=False,
            )
    response_json = response.model_dump_json()
    response_dict = json.loads(response_json)  
    response_text = response_dict.get("response", "")
    print(response_text)
    return response_text


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
student_pdf = "Student_Answer_Sheet.pdf"
student_text = extract_text_from_pdf(student_pdf)

# Teacher Extraction
teacher_pdf = "Answer_only.pdf"
teacher_text = extract_text_from_pdf(teacher_pdf)

# Final Results
output_feedback_pdf_path = "Student_Feedback.pdf"
feedback_text = evaluate_responses_with_gemini(teacher_text, student_text)
generate_feedback_pdf(feedback_text, output_feedback_pdf_path)


