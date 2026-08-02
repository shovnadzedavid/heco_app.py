import streamlit as str_module
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. გვერდის კონფიგურაცია (Wide layout იდეალურია რესპონსივობისთვის)
st.set_page_config(
    page_title="EduMed Pro - საზოგადოებრივი ჯანდაცვა და განათლება",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. რესპონსივობისა და დიზაინის გაძლიერებული CSS (მორგებულია მობილურზე, პლანშეტსა და დესკტოპზე)
st.markdown("""
<style>
    /* მთავარი კონტეინერის ფონი და სფეისინგი */
    .main { background-color: #f8fafc; padding: 1rem; }
    
    /* ღილაკების ადაპტაცია */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    
    /* მეტრიკების ქარდები */
    .metric-card { 
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
        padding: 20px; 
        border-radius: 12px; 
        color: white; 
        text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* მედია ქვერები სხვადასხვა მოწყობილობისთვის */
    @media (max-width: 768px) {
        /* მობილურის ეკრანებზე სათაურების და შრიფტების ზომის კორექტირება */
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.1rem !important; }
        .metric-card { padding: 10px; }
    }
</style>
""", unsafe_allow_html=True)

# სესიის ინიციალიზაცია
if "users" not in st.session_state:
    st.session_state.users = {
        "davitshovnadze": {"pass": "123", "role": "ლექტორი", "name": "დავით შოვნაძე", "email": "davit.shovnadze@uni.edu.ge"},
        "student1": {"pass": "123", "role": "სტუდენტი", "name": "გიორგი ბერიძე", "email": "g.beridze@student.uni.edu.ge"},
        "student2": {"pass": "123", "role": "სტუდენტი", "name": "ნინო მამულაშვილი", "email": "n.mamulashvili@student.uni.edu.ge"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"sender": "დავით შოვნაძე", "time": "13:00", "text": "მოგესალმებით ყველას! დღეს განვიხილავთ ეპიდემიოლოგიურ ზომებს."},
        {"sender": "გიორგი ბერიძე", "time": "13:02", "text": "გამარჯობა ბატონო დავით, მასალები გავეცანი."}
    ]

if "materials" not in st.session_state:
    st.session_state.materials = [
        {"title": "საზოგადოებრივი ჯანდაცვის საფუძვლები - ლექცია 1", "date": "2026-08-01", "type": "PDF"},
        {"title": "ეპიდემიოლოგიური კვლევის მეთოდები", "date": "2026-08-02", "type": "DOCX"}
    ]

if "ai_cases" not in st.session_state:
    st.session_state.ai_cases = [
        {"title": "ქეისი #1: ინფექციური აფეთქება რეგიონში", "content": "მუნიციპალიტეტში დაფიქსირდა კუჭ-ნაწლავის ინფექციების მატება. წყარო სავარაუდოდ წყალსადენია. რა ნაბიჯებს გადადგამდით პირველ რიგში?"}
    ]

if "student_messages" not in st.session_state:
    st.session_state.student_messages = []

# ავტორიზაციის გვერდი
def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>🩺 EduMed Pro</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #64748b;'>საზოგადოებრივი ჯანდაცვის საგანმანათლებლო პლატფორმა</h3>", unsafe_allow_html=True)
        st.write("---")
        
        with st.form("login_form"):
            st.subheader("ავტორიზაცია")
            username_input = st.text_input("მომხმარებლის სახელი (Username)")
            password_input = st.text_input("პაროლი (Password)", type="password")
            submit = st.form_submit_button("შესვლა")
            
            if submit:
                if username_input in st.session_state.users and st.session_state.users[username_input]["pass"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.success(f"მოგესალმებით, {st.session_state.users[username_input]['name']}!")
                    st.rerun()
                else:
                    st.error("მომხმარებლის სახელი ან პაროლი არასწორია!")
        
        st.info("💡 **სწრაფი ტესტირებისთვის:**\n* ლექტორი: `davitshovnadze` / `123`\n* სტუდენტი: `student1` / `123`")

if not st.session_state.logged_in:
    login_page()
else:
    current_user = st.session_state.username
    user_info = st.session_state.users[current_user]
    role = user_info["role"]
    name = user_info["name"]

    st.sidebar.markdown(f"### 👤 ავტორიზებულია: **{name}**")
    st.sidebar.markdown(f"სტატუსი: `🟢 {role}`")
    st.sidebar.write("---")

    if role == "ლექტორი":
        menu = st.sidebar.radio("სამუშაო მენიუ", [
            "მთავარი პანელი", 
            "სტუდენტების რეგისტრაცია/იმპორტი", 
            "მასალების ატვირთვა", 
            "AI ქეისების გენერაცია", 
            "სილაბუსის ქუიზები და შეფასება", 
            "შეტყობინებების მართვა", 
            "ლაივ ჩატი და შემოსულები"
        ])
    else:
        menu = st.sidebar.radio("სტუდენტის მენიუ", [
            "მთავარი მიმოხილვა", 
            "სასწავლო მასალები", 
            "სიმულაციური ქეისები", 
            "სიახლეები და თემები", 
            "შეტყობინების გაგზავნა ლექტორთან",
            "ლაივ ჩატი"
        ])

    st.sidebar.write("---")
    if st.sidebar.button("🚪 სისტემიდან გასვლა"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    # ლექტორის პანელი
    if role == "ლექტორი":
        if menu == "მთავარი პანელი":
            st.title("📊 ლექტორის პანელი - საზოგადოებრივი ჯანდაცვა")
            st.write(f"მოგესალმებით, ბატონო **{name}**. ეს არის თქვენი სამუშაო სივრცე.")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("<div class='metric-card'><h3>რეგისტრირებული სტუდენტები</h3><h2>150+</h2></div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='metric-card'><h3>აქტიური AI ქეისები</h3><h2>12</h2></div>", unsafe_allow_html=True)
            with c3:
                st.markdown("<div class='metric-card'><h3>ახალი წერილები</h3><h2>3</h2></div>", unsafe_allow_html=True)

        elif menu == "სტუდენტების რეგისტრაცია/იმპორტი":
            st.title("📁 სტუდენტთა Excel ფაილის იმპორტი & ავტომატური მეილები")
            st.write("ატვირთეთ Excel (.xlsx) ფაილი (`სახელი`, `გვარი`, `მეილი`). სისტემა დაგენერირებს იუზერებს (პაროლი: `123`).")
            
            uploaded_file = st.file_uploader("ატვირთეთ სტუდენტების Excel ფაილი", type=["xlsx", "xls"])
            
            sample_df = pd.DataFrame({
                "სახელი": ["ანი", "ლუკა"],
                "გვარი": ["გიორგაძე", "მიქაძე"],
                "მეილი": ["ani.giorgadze@student.uni.edu.ge", "luka.mikadze@student.uni.edu.ge"]
            })
            
            def convert_df_to_excel(df):
                from io import BytesIO
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                writer.close()
                return output.getvalue()
            
            st.download_button(
                label="📥 ჩამოტვირთეთ Excel-ის სანიმუშო შაბლონი",
                data=convert_df_to_excel(sample_df),
                file_name="students_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            if uploaded_file is not None:
                df = pd.read_excel(uploaded_file)
                st.write("აყვანილი მონაცემები:", df.head())
                
                if st.button("🚀 იუზერების გენერაცია და მეილების გაგზავნა"):
                    success_count = 0
                    for index, row in df.iterrows():
                        fname = row.get("სახელი", "User")
                        lname = row.get("გვარი", "")
                        email = row.get("მეილი", "")
                        username = f"{fname.lower()}_{lname.lower()}"
                        
                        st.session_state.users[username] = {
                            "pass": "123",
                            "role": "სტუდენტი",
                            "name": f"{fname} {lname}",
                            "email": email
                        }
                        success_count += 1
                            
                    st.success(f" წარმატებით დაგენერირდა {success_count} იუზერი და გაიგზავნა შეტყობინებები!")

        elif menu == "მასალების ატვირთვა":
            st.title("📂 საჯარო და სასწავლო მასალების ატვირთვა")
            mat_title = st.text_input("მასალის სათაური / აღწერა")
            uploaded_mat = st.file_uploader("ატვირთეთ ფაილი (PDF, DOCX, PPTX)", type=["pdf", "docx", "pptx", "png", "jpg"])
            
            if st.button("ატვირთვა სისტემაში"):
                if mat_title:
                    st.session_state.materials.append({
                        "title": mat_title,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "type": "ფაილი"
                    })
                    st.success(f"მასალა '{mat_title}' წარმატებით აიტვირთდა!")
                else:
                    st.warning("გთხოვთ მიუთითოთ მასალის სათაური.")
            
            st.write("---")
            st.subheader("არსებული მასალების სია:")
            for m in st.session_state.materials:
                st.write(f"📄 **{m['title']}** (ატვირთულია: {m['date']})")

        elif menu == "AI ქეისების გენერაცია":
            st.title("🤖 AI რეალურდრომიანი ქეისების გენერატორი")
            topic_input = st.text_input("მიუთითეთ თემა ან მიმართულება:")
            
            if st.button("✨ ქეისის გენერირება AI-ით"):
                if topic_input:
                    generated_case = f"ეპიდემიოლოგიური სიმულაცია თემაზე: '{topic_input}'. ანალიზი აჩვენებს რისკ-ფაქტორებს და რეკომენდებულ პრევენციულ ზომებს."
                    st.session_state.ai_cases.append({"title": f"ქეისი: {topic_input}", "content": generated_case})
                    st.success("ქეისი წარმატებით გენერირდა და გაუზიარდა სტუდენტებს!")
                else:
                    st.warning("გთხოვთ ჩაწეროთ თემა.")
                    
            st.write("### გენერირებული ქეისების არქივი:")
            for c in st.session_state.ai_cases:
                st.info(f"**{c['title']}**\n\n{c['content']}")

        elif menu == "სილაბუსის ქუიზები და შეფასება":
            st.title("📝 სილაბუსის სტანდარტების მართვა და ქუიზები")
            st.write("⚠️ **მხოლოდ ლექტორისთვის (დავით შოვნაძე)**")
            quiz_title = st.text_input("ქუიზის სახელი")
            quiz_q = st.text_area("ტესტური კითხვა ან შეფასების კრიტერიუმი:")
            if st.button("ქუიზის გამოქვეყნება სტუდენტებისთვის"):
                st.success(f"ქუიზი '{quiz_title}' წარმატებით შეიქმნა!")

        elif menu == "შეტყობინებების მართვა":
            st.title("📬 სტუდენტთა შემოსული წერილები")
            if not st.session_state.student_messages:
                st.info("შემოსული წერილები არ არის.")
            else:
                for idx, sm in enumerate(st.session_state.student_messages):
                    st.warning(f"**{sm['student']}**: {sm['text']} *(დრო: {sm['time']})*")

        elif menu == "ლაივ ჩატი და შემოსულები":
            st.title("💬 ლაივ ჩატი (Online)")
            st.success("🟢 **დავით შოვნაძე** (აქტიურია ახლა)")
            for msg in st.session_state.chat_messages:
                st.markdown(f"**{msg['sender']}** [{msg['time']}]: {msg['text']}")
            
            new_msg = st.text_input("მოიწერეთ შეტყობინება...")
            if st.button("გაგზავნა") and new_msg:
                st.session_state.chat_messages.append({"sender": name, "time": datetime.now().strftime("%H:%M"), "text": new_msg})
                st.rerun()

    # სტუდენტის პანელი
    else:
        if menu == "მთავარი მიმოხილვა":
            st.title(f"👋 გამარჯობა, {name}!")
            st.info("📚 ხელმისაწვდომია ახალი მასალები და სიმულაციური ქეისები.")

        elif menu == "სასწავლო მასალები":
            st.title("📖 ლექციები და სასწავლო მასალები")
            for m in st.session_state.materials:
                st.markdown(f"📄 **{m['title']}** — თარიღი: `{m['date']}`")

        elif menu == "სიმულაციური ქეისები":
            st.title("🧪 AI ქეისები")
            for c in st.session_state.ai_cases:
                st.warning(f"### {c['title']}\n{c['content']}")

        elif menu == "სიახლეები და თემები":
            st.title("🌍 გლობალური და ადგილობრივი სიახლეები")
            st.markdown("* ვაქცინაციის ახალი სახელმძღვანელოები 2026\n* ქრონიკული დაავადებების პრევენციის პოლიტიკა")

        elif menu == "შეტყობინების გაგზავნა ლექტორთან":
            st.title("✉️ პირდაპირი შეტყობინება ლექტორს")
            msg_text = st.text_area("თქვენი შეტყობინება ან კითხვა:")
            if st.button("გაგზავნა ლექტორს") and msg_text:
                st.session_state.student_messages.append({"student": name, "text": msg_text, "time": datetime.now().strftime("%Y-%m-%d %H:%M")})
                st.success("შეტყობინება გაეგზავნა ლექტორს!")

        elif menu == "ლაივ ჩატი":
            st.title("💬 ლაივ ჩატი")
            for msg in st.session_state.chat_messages:
                st.markdown(f"**{msg['sender']}** [{msg['time']}]: {msg['text']}")
            new_msg = st.text_input("მოიწერეთ შეტყობინება...")
            if st.button("გაგზავნა") and new_msg:
                st.session_state.chat_messages.append({"sender": name, "time": datetime.now().strftime("%H:%M"), "text": new_msg})
                st.rerun()
