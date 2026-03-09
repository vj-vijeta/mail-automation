import streamlit as st
import smtplib
import csv
import time
import io
import pandas as pd
import streamlit.components.v1 as components

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

from streamlit_quill import st_quill

# --- Page Configuration ---
st.set_page_config(page_title="Ei Mass Emailer", page_icon="✉️", layout="wide")
st.title("✉️ Professional Mass Email Campaigner")
st.write("Easily dispatch personalized updates, reports, and readiness data to schools.")

# --- 1. Credentials Sidebar ---
with st.sidebar:
    st.header("1. Server Credentials")
    st.info("💡 **Security Note:** Never use your primary login password. Generate an App-Specific Password in your Zoho Security Settings.")
    # Defaulting to the professional email domain format
    sender_email = st.text_input("Zoho Email Address", value="@ei.study")
    sender_password = st.text_input("Zoho App Password", type="password")

# --- 2. Compose Email ---
st.header("2. Design Your Email")

# Let the user choose their skill level / mode
compose_mode = st.radio(
    "Choose your editor mode:",
    ["🧱 Easy Builder (No Coding)", "💻 Paste Custom HTML Code"],
    horizontal=True
)

generated_html = ""
local_inline_img = None

if compose_mode == "🧱 Easy Builder (No Coding)":
    st.write("---")
    tab1, tab2 = st.tabs(["✍️ Edit Modules", "👁️ Live Preview"])

    with tab1:
        with st.expander("ℹ️ How to use the Easy Builder", expanded=False):
            st.write("""
            * **Personalization:** Type `{School Name}` anywhere to automatically insert the school's name from your CSV.
            * **Images:** Upload a local banner, and the app will embed it securely into the email body.
            * **Colors:** Click the color boxes to perfectly match the branding of Ei ASSET, Ei CARES, etc.
            """)
        
        # MODULE 1: Header Image
        st.subheader("🖼️ Module 1: Header Banner")
        col1, col2 = st.columns(2)
        with col1:
            local_inline_img = st.file_uploader("Upload Banner Image (PNG/JPG)", type=['png', 'jpg', 'jpeg'], key="easy_img")
        with col2:
            header_img_url = st.text_input("OR Paste a Public Image URL (Leaves file smaller)")
        
        img_src = "cid:inline_img" if local_inline_img else header_img_url

        # MODULE 2: Main Heading & Color
        st.subheader("🔤 Module 2: Heading")
        col3, col4 = st.columns([3, 1])
        with col3:
            heading_text = st.text_input("Heading Text", value="Important Readiness Update for {School Name}")
        with col4:
            heading_color = st.color_picker("Heading Color", "#0056b3") # Default professional blue

        # MODULE 3: Body Content (Rich Text)
        st.subheader("📝 Module 3: Message Body")
        st.caption("Use the toolbar to bold text, add lists, or change font colors.")
        body_text = st_quill(
            value="<p>Dear Administrator,</p><p>We are writing to provide a critical update regarding your current readiness status.</p><p>Please review the attached documents carefully to ensure a smooth deployment.</p><p>Best regards,<br>The Team</p>",
            html=True,
            key="quill_builder"
        )

        # MODULE 4: Call to Action Button
        st.subheader("🔘 Module 4: Call to Action Button")
        col5, col6, col7 = st.columns([2, 2, 1])
        with col5:
            button_text = st.text_input("Button Text", value="View Portal")
        with col6:
            button_link = st.text_input("Button Link (URL)", value="https://")
        with col7:
            button_color = st.color_picker("Button Color", "#0056b3")

    # Stitch the Easy Builder HTML together
    generated_html = f"""
    <div style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; overflow: hidden;">
        {f'<div style="background-color: #f4f6f8; text-align: center; border-bottom: 3px solid {heading_color};"><img src="{img_src}" style="max-width: 100%; height: auto; display: block;"></div>' if img_src else ''}
        <div style="padding: 30px;">
            {f'<h2 style="color: {heading_color}; margin-top: 0;">{heading_text}</h2>' if heading_text else ''}
            
            <div style="font-size: 15px; line-height: 1.6;">{body_text}</div>
            
            {f'<div style="text-align: center; margin-top: 30px;"><a href="{button_link}" style="background-color: {button_color}; color: #ffffff; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">{button_text}</a></div>' if button_text and button_link else ''}
        </div>
    </div>
    """

    with tab2:
        st.write("### Inbox Preview")
        preview_html = generated_html.replace("{School Name}", "Millennium World School")
        if local_inline_img:
            preview_html = preview_html.replace("cid:inline_img", "https://via.placeholder.com/600x150.png?text=Your+Uploaded+Banner+Will+Appear+Here")
        components.html(preview_html, height=500, scrolling=True)

else:
    # --- Advanced HTML Mode ---
    st.write("---")
    st.info("💡 **Pro Tip:** You can still use `{School Name}` in your custom HTML to personalize it. If you want to embed a local image, upload it below and use `<img src=\"cid:inline_img\">` in your code.")
    
    col_html1, col_html2 = st.columns([1, 1])
    with col_html1:
        local_inline_img = st.file_uploader("Optional: Upload an image to embed as 'cid:inline_img'", type=['png', 'jpg', 'jpeg'], key="html_img")
    
    html_tab, preview_tab = st.tabs(["💻 Paste HTML", "👁️ Live Preview"])
    
    with html_tab:
        generated_html = st.text_area("Paste your raw HTML code here:", height=400, value="<h1>Hello {School Name}</h1>\n<p>Your custom HTML goes here.</p>")
        
    with preview_tab:
        st.write("### Inbox Preview")
        preview_html = generated_html.replace("{School Name}", "Mount St. Mary'S School")
        if local_inline_img:
            preview_html = preview_html.replace("cid:inline_img", "https://via.placeholder.com/600x150.png?text=Your+Uploaded+Banner+Will+Appear+Here")
        components.html(preview_html, height=500, scrolling=True)

# --- 3. Subject & General Attachments ---
st.write("---")
st.header("3. Subject & File Attachments")
col8, col9 = st.columns(2)
with col8:
    subject = st.text_input("Email Subject", value="Important Update")
with col9:
    uploaded_attachments = st.file_uploader("Attach PDF Reports, Excel files, etc. (Sent to everyone)", accept_multiple_files=True)

# --- 4. Dispatch Center ---
st.write("---")
st.header("4. Upload CSV & Dispatch")
uploaded_csv = st.file_uploader("Upload Data (CSV must have exactly 'School Name' and 'Email' columns)", type="csv")

if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    data_tab, send_tab = st.tabs(["📊 Review Audience Data", "🚀 Launch Campaign"])
    
    with data_tab:
        st.metric("Total Schools to Contact", len(df))
        st.dataframe(df, use_container_width=True)
            
    with send_tab:
        st.warning("⚠️ Double-check your preview and data. Once you click send, the emails will be dispatched immediately.")
        if st.button("🚀 Confirm & Send Campaign", type="primary"):
            if not all([sender_email, sender_password, subject]):
                st.error("❌ Please ensure your Zoho credentials and Subject line are filled out.")
            else:
                rows = df.to_dict('records')
                progress_bar = st.progress(0)
                status_text = st.empty()
                log_container = st.container()
                
                try:
                    status_text.text("Connecting to secure Zoho Server...")
                    server = smtplib.SMTP("smtp.zoho.in", 587) # Ensure this matches your Zoho datacenter (.in vs .com)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    status_text.text("✅ Authentication successful! Dispatching emails...")
                    
                    total_emails = len(rows)
                    
                    for index, row in enumerate(rows):
                        school_name = row.get('School Name', 'Administrator')
                        recipient_email = row.get('Email')
                        
                        if pd.isna(recipient_email) or not str(recipient_email).strip():
                            log_container.write(f"⚠️ Skipped {school_name}: No valid email address.")
                            continue
                            
                        # Personalize the HTML
                        personalized_body = generated_html.replace("{School Name}", str(school_name))
                        
                        # Structure the email to support inline HTML images + standard file attachments
                        msg = MIMEMultipart('related')
                        msg['From'] = sender_email
                        msg['To'] = str(recipient_email)
                        msg['Subject'] = subject
                        
                        msg_alternative = MIMEMultipart('alternative')
                        msg.attach(msg_alternative)
                        msg_alternative.attach(MIMEText(personalized_body, 'html'))
                        
                        # Attach the inline image if the user uploaded one (works for both modes)
                        if local_inline_img:
                            local_inline_img.seek(0)
                            image = MIMEImage(local_inline_img.read(), name=local_inline_img.name)
                            image.add_header('Content-ID', '<inline_img>') 
                            image.add_header('Content-Disposition', 'inline')
                            msg.attach(image)
                        
                        # Attach general files (PDFs, etc.)
                        if uploaded_attachments:
                            for attached_file in uploaded_attachments:
                                attached_file.seek(0) 
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attached_file.read())
                                encoders.encode_base64(part)
                                part.add_header('Content-Disposition', f'attachment; filename="{attached_file.name}"')
                                msg.attach(part)
                        
                        # Send
                        server.send_message(msg)
                        log_container.write(f"✅ Dispatched to: {school_name} ({recipient_email})")
                        
                        progress_bar.progress((index + 1) / total_emails)
                        time.sleep(2) # Zoho rate-limit protection
                        
                    server.quit()
                    status_text.success("🎉 Campaign completely dispatched!")
                    
                except smtplib.SMTPAuthenticationError:
                    st.error("❌ Authentication Error: Invalid Zoho Email or App Password.")
                except Exception as e:
                    st.error(f"❌ A system error occurred: {e}")