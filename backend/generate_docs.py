import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_documentation():
    doc = Document()
    
    # Title
    title = doc.add_heading('LyzrNegotiate: Autonomous B2B Negotiation Platform', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph('Official System Documentation & Architecture Guide')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle_format = subtitle.runs[0].font
    subtitle_format.size = Pt(14)
    subtitle_format.italic = True
    
    doc.add_page_break()
    
    # 1. Overview
    doc.add_heading('1. Executive Overview', level=1)
    doc.add_paragraph(
        "LyzrNegotiate is a production-grade, multi-agent AI platform designed to automate B2B vendor and "
        "procurement negotiations. By leveraging Lyzr Agent Studio, the platform pits an autonomous AI Buyer "
        "against an autonomous AI Vendor to negotiate contract terms (Price, Delivery Days, and SLA Penalties) "
        "in real-time. This eliminates the weeks of email ping-pong typically required for enterprise B2B contracting."
    )
    
    # 2. Use Cases
    doc.add_heading('2. Primary Use Cases', level=1)
    doc.add_paragraph("This platform is designed for enterprise procurement and supply-chain teams. Key use cases include:")
    
    use_cases = [
        ("Procurement Automation", "Automatically haggle with software vendors, freelancers, or raw material suppliers to secure the best possible price without human intervention."),
        ("Dynamic Vendor Quoting", "Allow clients to immediately negotiate with your company's AI sales agent, providing instant concessions and finalizing contracts 24/7."),
        ("Safe AI Contracting", "Ensure that no AI agent ever agrees to a deal outside of strict financial limits, thanks to the mathematical guardrails enforced by the Safe AI Arbiter."),
        ("Tamper-Proof Audit Trails", "Automatically log every AI decision, concession, and justification to a persistent database and the AIMS governance layer for compliance tracking.")
    ]
    
    for term, desc in use_cases:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(f"{term}: ").bold = True
        p.add_run(desc)
        
    # 3. System Architecture
    doc.add_heading('3. System Architecture', level=1)
    doc.add_paragraph(
        "The application is decoupled into three primary layers ensuring security, scalability, and ease of deployment. "
        "The architecture follows a strict separation of concerns:"
    )
    
    doc.add_heading('Data Flow:', level=3)
    flow = [
        "1. The User configures policy bounds in the React Frontend.",
        "2. The Frontend sends a REST API request to the FastAPI Backend.",
        "3. The FastAPI Orchestrator initiates a negotiation loop.",
        "4. The Orchestrator calls the Lyzr Agent Studio API to get responses from the AI Buyer and AI Vendor.",
        "5. Before recording any bid, the Safe AI Arbiter mathematically validates the JSON payload.",
        "6. Validated bids are saved to the PostgreSQL Database and broadcast back to the Frontend UI.",
        "7. Upon consensus, the backend dynamically generates a legally formatted PDF contract."
    ]
    for step in flow:
        doc.add_paragraph(step, style='List Number')
        
    # 4. Component Breakdown
    doc.add_heading('4. Component Breakdown', level=1)
    
    doc.add_heading('4.1 The Frontend (React + Vite + TypeScript)', level=2)
    doc.add_paragraph("The frontend serves as the control center for human oversight, built with TailwindCSS for an enterprise SaaS feel.")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("Setup Dashboard: ").bold = True
    p.add_run("Users define strict policy bounds (Max Budget, Min SLA, Max Delivery).")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("Negotiation Arena: ").bold = True
    p.add_run("A real-time monitoring room tracking declining price curves via Recharts.")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("History Dashboard: ").bold = True
    p.add_run("A centralized view of all past negotiations to download finalized PDF contracts.")

    doc.add_heading('4.2 The Backend (FastAPI + Python + SQLAlchemy)', level=2)
    doc.add_paragraph("The backend acts as the secure 'referee' between the user, the database, and the AI agents.")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("The Orchestrator: ").bold = True
    p.add_run("Manages the turn-based conversation loop and database sessions.")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("Safe AI Arbiter: ").bold = True
    p.add_run("A deterministic, mathematical firewall that rejects any AI hallucination or out-of-bounds offer.")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("Contract Generation: ").bold = True
    p.add_run("Compiles the agreed-upon price, SLA, and delivery days into a legally formatted PDF using ReportLab.")

    doc.add_heading('4.3 The AI Layer (Lyzr Agent Studio)', level=2)
    doc.add_paragraph("Connects directly to the official Lyzr Agent Studio inference endpoints (v3/inference/chat/).")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("Personas: ").bold = True
    p.add_run("Agents are configured in the Lyzr Studio UI with specific negotiation tactics.")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("JSON Schemas: ").bold = True
    p.add_run("The agents are strictly prompted to output parsable JSON containing price, delivery, SLA, and justifications.")

    # 5. Deployment
    doc.add_heading('5. Cloud Deployment Strategy', level=1)
    doc.add_paragraph(
        "This project is optimized for modern Platform-as-a-Service (PaaS) providers to ensure a seamless "
        "hackathon deployment and presentation."
    )
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("Frontend: ").bold = True
    p.add_run("Hosted on Vercel utilizing the vercel.json routing rewrite for Single Page Applications.")
    p = doc.add_paragraph(style='List Bullet')
    p.add_run("Backend & DB: ").bold = True
    p.add_run("Hosted on Render using Render's free PostgreSQL managed database to prevent ephemeral disk wipes and guarantee persistence.")

    # Save
    output_path = os.path.join(os.path.dirname(__file__), 'LyzrNegotiate_Official_Documentation.docx')
    doc.save(output_path)
    print(f"Documentation generated successfully at: {output_path}")

if __name__ == '__main__':
    create_documentation()
