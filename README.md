SmartDMS – AI Powered Smart Document Management System

SmartDMS is an AI-powered document management platform that automatically reads, extracts, and organizes information from uploaded documents such as receipts, medical reports, bills, and PDFs.
Instead of manually entering data or managing scattered files, users can simply upload a document and the system will intelligently process it using OCR and AI to extract key information like names, amounts, dates, and expiry details. The extracted data is then structured, categorized, and stored securely, while also generating useful insights such as expense summaries and upcoming alerts.
The platform combines modern web technologies with artificial intelligence to create a seamless document automation workflow.

Deployment Note

Deploy the React frontend to Netlify and deploy the FastAPI backend separately on a Python-friendly platform such as Render, Railway, or Vercel. In Netlify, set `VITE_API_BASE_URL` to your backend URL including the `/api` suffix, for example `https://your-backend.example.com/api`.

Key Features
AI Document Understanding

Automatically extracts important information such as:
Names
Dates
Amounts
Vendor names
Policy numbers
Expiry dates from images and PDF documents.
Automatic Document Categorization

Documents are automatically organized into categories such as:
Bills
Medical
Insurance
Banking
Education
Legal
Smart Alerts System
Detects important deadlines like:
Bill due dates
Insurance expiry
Warranty expiration
and notifies users through the dashboard.
Expense Tracking
Analyzes receipts and invoices to generate spending insights.
Document Timeline
Provides a chronological timeline of document uploads and highlights upcoming important dates.

Secure User Authentication
Includes a login and signup system with encrypted password storage.
Modern Dashboard Interface

Interactive dashboard displaying:
Document statistics
Expense summaries
Alerts and reminders
Document history

Tech Stack
Frontend
React (Vite) – User interface and SPA architecture
Tailwind CSS – Styling and UI design
React Router – Navigation between pages
Axios – Communication with backend APIs
Lucide React – Icons for UI components

Backend
FastAPI – High-performance Python API framework
Uvicorn – ASGI server to run FastAPI
SQLite – Lightweight database for storing users and documents
bcrypt / passlib – Secure password hashing
AI & Document Processing
OpenCV – Image preprocessing and enhancement
EasyOCR – Optical Character Recognition to extract text
PyMuPDF – Extract text from PDF documents
Google Gemini API – AI-powered extraction and categorization of document data

Project Architecture
Frontend (React)
        ↓
FastAPI Backend
        ↓
Document Processing Pipeline
        ↓
OCR + AI Extraction
        ↓
SQLite Database

Document Processing Pipeline
User uploads an image or PDF document.
The frontend sends the file to the FastAPI backend.
The backend preprocesses the document using OpenCV.
EasyOCR extracts raw text from the document.
Google Gemini AI analyzes the text and converts it into structured data.
The AI categorizes the document into predefined folders.
Extracted data and document metadata are stored in the SQLite database.
The frontend dashboard displays results, insights, and alerts.

How to Run the Project Locally

Follow these steps if you want to run the project on your system.

1. Clone the Repository
  https://github.com/Meemansa2601/Smart-Document-Management-System

 cd SmartDMS

2. Setup the Backend

Install Python dependencies:

cd backend
pip install -r requirements.txt

Create a .env file and add your API key:

GEMINI_API_KEY=your_api_key_here

Start the backend server:

uvicorn main:app --reload

The backend will run at:

http://127.0.0.1:8000


3. Setup the Frontend

Open a new terminal and run:

cd frontend
npm install
npm run dev

The frontend will start at:

http://localhost:5173
Usage

Create a new account using the signup page.

Log in to the dashboard.

Upload a document such as a receipt or PDF.

The system will automatically extract and categorize the document data.

View extracted information, expense insights, and alerts in the dashboard.

Future Improvements

Cloud document storage

Mobile application

Multi-language OCR support

Email and notification reminders

Advanced analytics and expense prediction

License

This project is intended for educational and research purposes.





