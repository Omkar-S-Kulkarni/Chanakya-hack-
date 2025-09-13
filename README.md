# Chanakya Hackathon #

# Agentic AI for Healthcare 

A multi-agent AI system designed to provide safe, reliable, and understandable healthcare assistance for both patients and clinicians.

## The Problem

Navigating healthcare is complex. Patients often struggle to understand complex medical documents and terminology, leading to confusion and non-adherence. Clinicians, on the other hand, face immense documentation burdens that contribute to burnout. Existing AI solutions often act as black boxes, providing answers without transparency or a verifiable safety net, making them unsuitable for high-stakes medical applications.

## Our Solution

The Agentic Healthcare Copilot is a suite of five specialized AI skills unified under a sophisticated two-agent architecture. 

* **Agent 1 (The Analyst):** Performs the primary analysis. It can translate lab reports, check for drug interactions, triage symptoms, analyze chronic care data, and summarize clinical notes.
* **Agent 2 (The Reviewer):** Acts as a real-time quality and safety auditor. It evaluates the output of Agent 1 against a set of critical criteria (Clarity, Safety, Actionability, Completeness), providing a meta-analysis of the AI's own work.

This system is built on a safety-first principle, combining deterministic rule engines with a powerful Retrieval-Augmented Generation (RAG) pipeline to ensure all outputs are grounded, transparent, and reliable.

## Key Features

* **Drug Safety & Dosage Agent:** Checks medications for interactions, duplicate therapies, and allergies using a local database.
* **Doctor-to-Patient Translator:** Translates complex lab reports and prescriptions from PDF or images into plain language using multimodal AI.
* **Symptom Urgency Triage:** Provides a preliminary triage recommendation (Home Care, GP, ER) based on user-described symptoms, with hard-coded red flag detection.
* **Chronic Care Coach:** Analyzes logs of vitals (e.g., blood pressure) from spreadsheets to identify trends and provide behavioral nudges.
* **Doctor's Co-Pilot:** Processes clinical encounter notes to generate SOAP summaries, check against stored guidelines, and draft orders.
* **Two-Agent Evaluation Workflow:** Every output from the primary agent is reviewed by a second AI agent for quality and safety, and the evaluation is presented to the user.

## Architecture

The system operates on a three-layer logic model:
1.  **Deterministic Rules:** A fast, hard-coded `RuleEngine` catches undeniable safety issues (e.g., severe drug interactions, critical symptoms) before the LLM is involved.
2.  **Retrieval-Augmented Generation (RAG):** User queries are augmented with relevant context retrieved from a local, curated Knowledge Base built from real medical documents. This grounds the AI's responses in facts and minimizes hallucinations.
3.  **Generative Reasoning:** The Google Gemini Pro model is used for sophisticated reasoning, summarization, multimodal understanding, and generating human-friendly responses.

## Tech Stack

* **Backend:** Python, Flask
* **Frontend:** Streamlit
* **AI Model:** Google Gemini Pro API
* **Knowledge Base / RAG:** FAISS, Sentence-Transformers, LangChain
* **Data Processing:** Pandas, PyMuPDF, EasyOCR, ScispaCy
* **Core Libraries:** requests, python-dotenv

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Prerequisites
* Python 3.10+
* Git

### 2. Clone the Repository
```bash
git clone <your-repository-url>
cd Chanakya-hack-