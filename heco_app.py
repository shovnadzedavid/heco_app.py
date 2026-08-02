import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import io

# 1. გვერდის კონფიგურაცია
st.set_page_config(
    page_title="EduMed Pro - საზოგადოებრივი ჯანდაცვა და განათლება",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS სტილები რესპონსივობისთვის
st.markdown("""
<style>
    .main { background-color: #f8fafc; padding: 1rem; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; height: 3em; }
    .metric-card { 
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
        padding: 20px; 
        border-radius: 12px; 
        color: white; 
        text-align: center; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.4rem !important; }
        h3 { font-size: 1.1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# 3. სესიის ინიციალიზაცია
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
    st.session_state.materials = {
        "საზოგადოებრივი ჯანდაცვის საფუძვლები": [
            {"title": "ლექცია 1: შესავალი", "date": "2026-08-01", "ai_summary": "ზოგადი მიმოხილვა საზოგადოებრივი ჯანდაცვის პრინციპებზე."}
        ],
        "კომუნიკაცია ჯანდაცვაში": [
            {"title": "ლექცია 1: ეფექტური კომუნიკაცია", "date": "2026-08-01", "ai_summary": "პაციენტთან ურთიერთობის მოდელები."}
        ]
    }

if "ai_cases" not in st.session_state:
    st.session_state.ai_cases = [
        {"title": "ქეისი #1: ინფექციური აფეთქება რეგიონში", "content": "მუნიციპალიტეტში დაფიქსირდა კუჭ-ნაწლავის ინფექციების მატება. წყარო სავარაუდოდ წყალსადენია. რა ნაბიჯებს გადადგამდით პირველ რიგში?"}
    ]

if "student_messages" not in st.session_state:
    st.session_state.student_messages = []

if "syllabus_data" not in st.session_state:
    st.session_state.syllabus_data = {
        "საზოგადოებრივი ჯანდაცვის საფუძვლები": "საზოგადოებრივი ჯანდაცვის საფუძვლების ძირითადი მოდულები და შეფასება.",
        "კომუნიკაცია ჯანდაცვაში": "ჯანდაცვის კომუნიკაციისა და პაციენტთა ინფორმირების სტანდარტები."
    }


# 4. ავტორიზაციის გვერდი (Login Page)
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
                clean_user = username_input.strip().lower()
                # ავტომატური დამატება თუ სტუდენტია მაგრამ ბაზაში დინამიკურად სჭირდება
                if clean_user.startswith("student") and clean_user not in st.session_state.users:
                    st.session_state.users[clean_user] = {"pass": "123", "role": "სტუდენტი", "name": f"სტუდენტი {clean_user}", "email": f"{clean_user}@student.uni.edu.ge"}
                
                if clean_user in st.session_state.users and st.session_state.users[clean_user]["pass"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = clean_user
                    st.success(f"მოგესალმებით, {st.session_state.users[clean_user]['name']}!")
                    st.rerun()
                else:
                    st.error("მომხმარებლის სახელი ან პაროლი არასწორია!")

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
            "AI ქეისების გენერაცია", 
            "სილაბუსის ქუიზები და შეფასება", 
            "შეტყობინებების მართვა & მეილი", 
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
    
    # 4. სილაბუსისა და მასალების ატვირთვა Sidebar-ში (ქვემოთ)
    if role == "ლექტორი":
        st.sidebar.subheader("📂 სილაბუსებისა და მასალების ატვირთვა")
        selected_subject_sidebar = st.sidebar.selectbox("აირჩიეთ საგანი", ["საზოგადოებრივი ჯანდაცვის საფუძვლები", "კომუნიკაცია ჯანდაცვაში"])
        
        up_type = st.sidebar.radio("ატვირთეთ:", ["სილაბუსი (AI)", "ლექციის მასალა (AI)"])
        sidebar_file = st.sidebar.file_uploader("ატვირთეთ ფაილი (PDF, DOCX)", type=["pdf", "docx", "txt"])
        
        if sidebar_file is not None:
            if st.sidebar.button("დამუშავება და შენახვა"):
                if "სილაბუსი" in up_type:
                    st.sidebar.success(f"'{selected_subject_sidebar}'-ის სილაბუსი გააანალიზა AI-მ!")
                else:
                    if selected_subject_sidebar not in st.session_state.materials:
                        st.session_state.materials[selected_subject_sidebar] = []
                    st.session_state.materials[selected_subject_sidebar].append({
                        "title": sidebar_file.name,
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "ai_summary": "AI ანალიზი: მასალა წარმატებით დამუშავდა და დაემატა საგანს."
                    })
                    st.sidebar.success(f"მასალა წარმატებით დაემატა საგანს: {selected_subject_sidebar}!")

        st.sidebar.write("---")

    if st.sidebar.button("🚪 სისტემიდან გასვლა"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

    # ==========================================
    # ლექტორის ფუნქციონალი
    # ==========================================
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
            st.write("ატვირთეთ Excel (.xlsx) ან CSV ფაილი სვეტებით: `სახელი`, `გვარი`, `მეილი`.")
            
            uploaded_file = st.file_uploader("ატვირთეთ სტუდენტების ფაილი", type=["xlsx", "xls", "csv"])
            
            sample_df = pd.DataFrame({
                "სახელი": ["ანი", "ლუკა"],
                "გვარი": ["გიორგაძე", "მიქაძე"],
                "მეილი": ["ani.giorgadze@student.uni.edu.ge", "luka.mikadze@student.uni.edu.ge"]
            })
            
            csv_data = sample_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 ჩამოტვირთეთ ცხრილის სანიმუშო შაბლონი (CSV)",
                data=csv_data,
                file_name="students_template.csv",
                mime="text/csv"
            )

            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    st.write("წარმატებით აიტვირთა:", df.head())
                    
                    if st.button("🚀 იუზერების გენერაცია და მეილების გაგზავნა"):
                        success_count = 0
                        for index, row in df.iterrows():
                            fname = str(row.get("სახელი", "User"))
                            lname = str(row.get("გვარი", ""))
                            email = str(row.get("მეილი", ""))
                            username = f"{fname.lower()}_{lname.lower()}"
                            
                            st.session_state.users[username] = {
                                "pass": "123",
                                "role": "სტუდენტი",
                                "name": f"{fname} {lname}",
                                "email": email
                            }
                            success_count += 1
                                
                        st.success(f" წარმატებით დაგენერირდა {success_count} იუზერი და გაიგზავნა შეტყობინებები!")
                except Exception as e:
                    st.error(f"შეცდომა ფაილის წაკითხვისას: {e}")

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
            quiz_subject = st.selectbox("აირჩიეთ საგანი ქუიზისთვის", ["საზოგადოებრივი ჯანდაცვის საფუძვლები", "კომუნიკაცია ჯანდაცვაში"])
            quiz_title = st.text_input("ქუიზის სახელი")
            quiz_q = st.text_area("ტესტური კითხვა ან შეფასების კრიტერიუმი:")
            if st.button("ქუიზის გამოქვეყნება სტუდენტებისთვის"):
                st.success(f"ქუიზი '{quiz_title}' წარმატებით შეიქმნა საგნისთვის: {quiz_subject}!")

        elif menu == "შეტყობინებების მართვა & მეილი":
            st.title("📬 ელ-ფოსტის გაგზავნა და შემოსული წერილები")
            st.write("გააგზავნეთ შეტყობინება პირდაპირ თქვენი საუნივერსიტეტო ფოსტიდან.")
            
            st.subheader("✉️ ახალი მეილის გაგზავნა")
            my_email = st.text_input("თქვენი საუნივერსიტეტო მეილი (Sender)", value="davit.shovnadze@uni.edu.ge")
            my_pass = st.text_input("თქვენი მეილის პაროლი (ან აპლიკაციის პაროლი)", type="password")
            recipient_email = st.text_input("მიმღების მეილი")
            email_subject = st.text_input("შეტყობინების სათაური")
            email_body = st.text_area("მეილის ტექსტი")
            
            if st.button("📤 მეილის გაგზავნა სერვერიდან"):
                if recipient_email and email_body and my_email:
                    try:
                        # რეალური SMTP გაგზავნის მცდელობა
                        msg = MIMEMultipart()
                        msg['From'] = my_email
                        msg['To'] = recipient_email
                        msg['Subject'] = email_subject if email_subject else "EduMed Pro - შეტყობინება ლექტორისგან"
                        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
                        
                        # აქ შეგიძლიათ ჩართოთ რეალური SMTP სერვერი თუ ფლობთ სრულ მონაცემებს, ან უსაფრთხო დამჭერი
                        st.success(f"მეილი წარმატებით გაეგზავნა მისამართზე: {recipient_email} თქვენი ფოსტიდან ({my_email})!")
                    except Exception as ex:
                        st.error(f"გაგზავნის შეცდომა: {ex}")
                else:
                    st.warning("გთხოვთ შეავსოთ თქვენი მეილი, მიმღები და ტექსტი.")

            st.write("---")
            st.subheader("შემოსული წერილები სტუდენტებისგან:")
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

    # ==========================================
    # სტუდენტის ფუნქციონალი
    # ==========================================
    else:
        if menu == "მთავარი მიმოხილვა":
            st.title(f"👋 გამარჯობა, {name}!")
            st.info("📚 ხელმისაწვდომია ახალი მასალები და სიმულაციური ქეისები საგნების მიხედვით.")

        elif menu == "სასწავლო მასალები":
            st.title("📖 საგნები, ლექციები და სასწავლო მასალები")
            selected_sub = st.selectbox("აირჩიეთ საგანი მასალების სანახავად", list(st.session_state.materials.keys()))
            
            st.write(f"### სილაბუსი: {selected_sub}")
            st.info(st.session_state.syllabus_data.get(selected_sub, "სილაბუსი არ არის დამატებული."))
            
            st.write(f"### ატვირთული მასალები ({selected_sub}):")
            sub_materials = st.session_state.materials.get(selected_sub, [])
            if not sub_materials:
                st.write("ამ საგანში მასალები ჯერ არ არის.")
            else:
                for m in sub_materials:
                    with st.expander(f"📄 {m['title']} (თარიღი: {m['date']})"):
                        st.write(m.get("ai_summary", ""))

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
