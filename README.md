This repository contains my submission for the Palindrome Data **AI Solutions Engineer** interview assessment.

---

## Overview

The core deliverable is a **single Python notebook** that:

1. Loads and parses the dataset of synthetic WhatsApp-style conversations.
2. Applies two rule-based models to generate:
   - An **HIV acquisition risk score**
   - A **Mental health risk score**
3. Produces:
   - A **recommendation summary**
   - A **treatment plan** aligned with general South African public-sector guidelines  
     *(non-clinical, for demonstration only)*

**Main Notebook:**  
**`palindrome_assessment_notebook.ipynb`**

---

## Repository Structure

- palindrome_assessment_notebook.ipynb # Main assessment notebook
- health_ai_whatsapp_100_conversations_long.txt

api/ # (Additional) FastAPI microservice
- main.py
  
streamlit_app/ # (Additional) Streamlit demo UI
- app.py
