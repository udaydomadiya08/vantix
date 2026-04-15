import google.generativeai as genai
import os
from fpdf.enums import XPos, YPos
# Set your Gemini API key
GEMINI_API_KEY = "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw"



genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-05-20')
def generate_subsections(topic, chapter_title):
    prompt = f"""
    For the chapter titled '{chapter_title}' in an eBook about {topic}, 
    create a detailed list of 3 to 5 subsection titles only. Output plain text, 
    each subsection title on a new line.
    """
    response = model.generate_content(prompt)
    subsections = [line.strip() for line in response.text.split('\n') if line.strip()]
    return subsections
def generate_subsection_content(topic, chapter_title, subsection_title):
    prompt = f"""
    Write a detailed section for the subsection '{subsection_title}' under the chapter '{chapter_title}' in an eBook about {topic}.
    Do NOT include bold text or markdown symbols like ** or __. or * also, jsut plain normal text
    Do NOT include subsection or chapter titles in the content. MIND IT!
    Start directly with the explanation.
    Use clear, friendly language with examples and a summary.
    Minimum 200 words.
    Only plain text output.
    """
    response = model.generate_content(prompt)
    content = response.text.strip()
    return content
def build_chapter_with_subsections(topic, chapter_title):
    subsections = generate_subsections(topic, chapter_title)
    full_content = ""
    for subsection in subsections:
        sub_content = generate_subsection_content(topic, chapter_title, subsection)
        
        # Remove the subsection title from sub_content if present (case insensitive)
        # Using replace to remove the title if it appears at start or anywhere
        # You can fine tune this if you want stricter matching (e.g., only at start)
        title = subsection.strip()
        
        # Remove exact match or title with trailing newlines/spaces
        if sub_content.lower().startswith(title.lower()):
            # Remove the title from the start and strip any leading whitespace/newlines
            sub_content = sub_content[len(title):].lstrip('\n ').rstrip('\n ')
        
        # Now add the subsection title explicitly, then the cleaned content
        full_content += f"\n{subsection}\n\n{sub_content}\n\n"

    return full_content.strip()

def generate_outline(topic):
    prompt = f"Create a detailed chapter-wise eBook outline for the topic: {topic}. only that and nothing else okay mindi t every chapter should have a clear chapter heading only  in new line and nothing else, max 3 chapters onl yand not more than that, only plain text dont use bold text"
    response = model.generate_content(prompt)
    return response.text

def generate_chapter(topic, chapter_title):
    prompt = f"""
    Write a full, detailed chapter for the title '{chapter_title}' for an eBook about {topic}.
    Do NOT include bold text or markdown symbols like ** or __.
    Do NOT repeat the chapter title in the content.
    Start directly with an introduction and structure the chapter with multiple paragraphs, practical examples, tips, and a short summary at the end.
    Use a friendly, clear tone.
    Only plain text output. Minimum 500 words.
    """
    response = model.generate_content(prompt)
    content = response.text.strip()

    # Post-cleaning: remove bold symbols and repeated title if any
    cleaned = content.replace("**", "").replace("__", "")
    if chapter_title in cleaned.split('\n')[0]:
        cleaned = '\n'.join(cleaned.split('\n')[1:]).strip()

    return cleaned


def generate_sales_copy(topic):
    prompt = f"Write an attractive sales page description for an eBook on '{topic}'."
    response = model.generate_content(prompt)
    return response.text

from fpdf import FPDF
from fpdf import FPDF
from fpdf.enums import XPos, YPos

from fpdf import FPDF
from fpdf.enums import XPos, YPos

class MyPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.current_chapter_title = ""
        self.chapter_page = 0

    def start_chapter(self, title):
        self.current_chapter_title = title
        self.chapter_page = 0

    def header(self):
        if self.chapter_page == 1:
            self.set_font('DejaVu', '', 10)
            self.set_y(10)  # vertical position from top

            # Title centered horizontally at top
            self.cell(0, 10, self.current_chapter_title, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

            # Page number at same vertical position but aligned right
            self.cell(0, 10, str(self.page_no()), new_x=XPos.RIGHT, new_y=YPos.TOP, align='R')

            # Explicitly set Y-position further down to create space before page content
            self.set_y(25)  # adjust this value as needed (e.g., 25 to put ~15 units below 10)


    def add_chapter_first_page(self, content):
        self.add_page()
        self.chapter_page = 1
        self.set_font('DejaVu', '', 24)
        title_y = self.h / 4
        self.set_y(title_y)
        
        # Use multi_cell to wrap chapter title
        self.multi_cell(0, 12, self.current_chapter_title, align='C')
        
        self.ln(10)
        self.set_line_width(0.7)
        self.line(20, self.get_y(), self.w - 20, self.get_y())
        self.ln(30)
        self.set_font('DejaVu', '', 12)
        self.multi_cell(0, 8, content)



    def add_chapter_page(self, content):
        self.add_page()
        self.chapter_page += 1
        self.set_font('DejaVu', '', 12)
        lines = content.split('\n')
        for line in lines:
            if line.strip() == "":
                self.ln(5)
            elif line.isupper() or len(line.split()) < 8:
                # Assume subsection title (simple heuristic)
                self.set_font('DejaVu', 'B', 14)
                self.cell(0, 10, line.strip())
                self.ln(8)
                self.set_font('DejaVu', '', 12)
            else:
                self.multi_cell(0, 8, line)

       
def save_ebook_pdf(title, chapters, chapters_list, subsections_dict, output_file):
    pdf = MyPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=20, top=20, right=20)
    pdf.add_font('DejaVu', '', '/Users/uday/Downloads/dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf')

    # Title page
    pdf.add_page()
    pdf.set_font('DejaVu', '', 24)
    pdf.cell(0, 20, title, align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, "An eBook Generated with AI", align='C', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(20)

    # Table of Contents
    pdf.add_page()
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, "Table of Contents", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    pdf.set_font('DejaVu', '', 12)
    
    for chapter_title in chapters_list:
        # Chapter title
        pdf.cell(0, 10, chapter_title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Subsections indented, smaller font
        subsections = subsections_dict.get(chapter_title, [])
        pdf.set_font('DejaVu', '', 10)
        for subsection in subsections:
            pdf.set_x(pdf.l_margin + 10)  # indent subsections by 10 user units (points)
            pdf.cell(0, 8, f"{subsection}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('DejaVu', '', 12)  # reset font size for next chapter

    # Add chapters content pages
    for i, chapter_content in enumerate(chapters):
        chapter_title = chapters_list[i]
        pdf.start_chapter(chapter_title)
        pdf.add_chapter_first_page(chapter_content)

    pdf.output(output_file)
    print(f"✅ Saved PDF: {output_file}")







def automate_ebook_creation(topic):
    print(f"🔍 Generating outline for: {topic}")
    outline_text = generate_outline(topic)
    chapters_list = [line.strip() for line in outline_text.split("\n") if line.strip()]
    
    subsections_dict = {}
    chapters_content = []

    for chapter_title in chapters_list:
        print(f"📝 Generating chapter and subsections: {chapter_title}")
        subsections = generate_subsections(topic, chapter_title)
        subsections_dict[chapter_title] = subsections
        
        content = build_chapter_with_subsections(topic, chapter_title)
        print(f"🔎 Content Preview for '{chapter_title}':", repr(content[:300]))
        chapters_content.append(content)



    ebook_filename = f"{topic.replace(' ', '_')}.pdf"
    save_ebook_pdf(topic.title(), chapters_content, chapters_list, subsections_dict, ebook_filename)


    sales_text = generate_sales_copy(topic)
    with open(f"{topic.replace(' ', '_')}_sales.txt", "w") as f:
        f.write(sales_text)

    print("🎉 Done! eBook and sales copy saved.")

topic = "Mastering Mindfulness for Beginners"
automate_ebook_creation(topic)

# with open("topics.txt") as file:
#     topics = [line.strip() for line in file if line.strip()]

# for topic in topics:
#     automate_ebook_creation(topic)
