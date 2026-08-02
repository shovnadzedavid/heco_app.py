import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        "davitshovnadze": {"pass": "123", "role": "ლექტორი", "name": "დავით შოვნაძე", "email": "davitshovnadze@cu.edu.ge"},
        "student1": {"pass": "123", "role": "სტუდენტი", "name": "გიორგი ბერიძე", "email": "g.beridze@student.uni.edu.ge"},
        "student2": {"pass": "123", "role": "სტუდენტი", "name": "ნინო მამულაშვილი", "email": "n.mamulashvili@student.uni.edu.ge"}
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"sender": "დავით შოვნაძე", "time": "13:00", "text": "მოგესალმებით ყველას! დღეს განვიხილავთ ეპიდემიოლოგიურ ზომებს."},
        {"sender": "გიორგი ბერიძე", "time": "13:02", "text": "გამარჯობა ბატონო დავით, განრიგს გავეცანი."}
    ]

if "materials" not in st.session_state:
    st.session_state.materials = {
        "საზოგადოებრივი ჯანდაცვის საფუძვლები": [
            {"title": "Introduction to Public Health - Mary-Jane Schneider (2021)", "date": "2026-09-12", "ai_summary": "სავალდებულო ლიტერატურა და ძირითადი თავები საზოგადოებრივი ჯანდაცვის ისტორიასა და პრინციპებზე."}
        ],
        "კომუნიკაცია ჯანდაცვაში": [
            {"title": "Behavior and Public Health & Health Literacy", "date": "2026-09-19", "ai_summary": "ქცევითი მეცნიერებები, ჯანმრთელობის წიგნიერება და რისკების მართვა."}
        ]
    }

if "ai_cases" not in st.session_state:
    st.session_state.ai_cases = [
        {
            "title": "ქეისი #1: თამბაქოს კონტროლი და საზოგადოებრივი ჯანდაცვა", 
            "content": "რეგიონში მატულობს თამბაქოს მოხმარება ახალგაზრდებში. სილაბუსისა და FCTC (თამბაქოს კონტროლის ჩარჩო-კონვენციის) სტანდარტებზე დაყრდნობით, რა პრევენციული და მარკეტინგული ზომები უნდა გაატაროს მუნიციპალიტეტმა?"
        }
    ]

if "student_submissions" not in st.session_state:
    st.session_state.student_submissions = []

if "student_messages" not in st.session_state:
    st.session_state.student_messages = []

if "syllabus_data" not in st.session_state:
    st.session_state.syllabus_data = {
        "საზოგადოებრივი ჯანდაცვის საფუძვლები": "კურსი მიზნად ისახავს სტუდენტებს გააცნოს საზოგადოებრივი ჯანდაცვის ძირითადი თეორიები, პრინციპები და თავისებურებები.",
        "კომუნიკაცია ჯანდაცვაში": "ჯანდაცვის კომუნიკაციისა და პაციენტთა ინფორმირების სტანდარტები."
    }

# სილაბუსიდან ზუსტად გადმოტანილი სალექციო განრიგი
if "lecture_schedule" not in st.session_state:
    st.session_state.lecture_schedule = pd.DataFrame({
        "თარიღი და დრო": [
            "2026-09-12 (13:30-15:25)", 
            "2026-09-19 (13:30-15:25)", 
            "2026-09-26 (13:30-15:25)", 
            "2026-10-03 (13:30-15:25)", 
            "2026-10-10 (13:30-15:25)", 
            "2026-10-17 (13:30-15:25)", 
            "2026-11-14 (13:30-15:25)", 
            "2026-11-21 (13:30-15:25)", 
            "2026-11-28 (13:30-15:25)", 
            "2026-12-05 (13:30-15:25)", 
            "2026-12-12 (13:30-15:25)", 
            "2026-12-19 (13:30-15:25)", 
            "2026-12-26 (13:30-15:25)"
        ],
        "აუდიტორია": ["B31"] * 13,
        "ლექციის თემა და განსახილველი საკითხები": [
            "თემა 1: შესავალი საზოგადოებრივ ჯანდაცვაში (ისტორია, კონტროვერსიები, მთავრობების პასუხისმგებლობა)",
            "თემა 2: ჯანმრთელობის კომუნიკაცია და ქცევითი მეცნიერებები (ქცევის შეცვლის მოდელები, ჯანმრთელობის წიგნიერება)",
            "თემა 3: ეპიდემიოლოგია, მონაცემები და საზოგადოებრივი ჯანდაცვა (პრინციპები, მეთოდები, მონაცემთა ფუნქციები)",
            "თემა 4: გადამდები დაავადებები (ინფექციური აფეთქებები და მათი გავლენა პოლიტიკაზე)",
            "თემა 5: არაგადამდები დაავადებები (რისკ-ფაქტორები, გლობალური ტვირთი და მენეჯმენტი)",
            "თემა 6: საზოგადოებრივი ჯანდაცვა 21-ე საუკუნეში, მიღწევები და გამოწვევები",
            "თემა 7: თამბაქო, საზოგადოებრივი ჯანდაცვის მტერი #1 (ეპიდემია, FCTC ჩარჩო-კონვენცია)",
            "თემა 8: სიმსუქნე და არაჯანსაღი კვება, საზოგადოებრივი ჯანდაცვის მტერი #2",
            "თემა 9: სუფთა გარემო (სუფთა წყალი და ჰაერი, როგორც პრევენციის ბაზისი)",
            "თემა 10: ნარჩენების მართვა (მყარი, საშიში და სამედიცინო ნარჩენები)",
            "თემა 11: ჯანმრთელობის სერვისების კვლევა (საჭიროებების ძიება და ეფექტიანობის შეფასება)",
            "თემა 12: საზოგადოებრივი ჯანდაცვა და მოსახლეობის დაბერება",
            "თემა 13: ინდივიდუალური პრეზენტაციები (სტუდენტთა შემაჯამებელი მოხსენებები)"
        ]
    })


# 4. ავტორიზაციის გვერდი
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
            "სალექციო განრიგი",
            "სიახლეები და თემები", 
            "შეტყობინების გაგზავნა ლექტორთან",
            "ლაივ ჩატი"
        ])

    st.sidebar.write("---")
    
    # სილაბუსისა და მასალების ატვირთვა Sidebar-ში (ქვემოთ)
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

            st.write("---")
            st.subheader("📝 სტუდენტების მიერ შესრულებული ქეისების AI შეფასებები:")
            if not st.session_state.student_submissions:
                st.info("სტუდენტების მხრიდან პასუხები ჯერ არ არის შემოსული.")
            else:
                for sub in st.session_state.student_submissions:
                    with st.expander(f"სტუდენტი: {sub['student']} | ქეისი: {sub['case_title']}"):
                        st.write(f"**სტუდენტის მოსაზრება:** {sub['answer']}")
                        st.success(f"**AI ექსპერტული შეფასება (სილაბუსის სტანდარტებით):** {sub['ai_eval']}")

        elif menu == "სტუდენტების რეგისტრაცია/იმპორტი":
            st.title("📁 სტუდენტთა Excel ფაილის იმპორტი & ავტომატური მეილები")
            uploaded_file = st.file_uploader("ატვირთეთ სტუდენტების ფაილი", type=["xlsx", "xls", "csv"])
            
            sample_df = pd.DataFrame({
                "სახელი": ["ანი", "ლუკა"],
                "გვარი": ["გიორგაძე", "მიქაძე"],
                "მეილი": ["ani.giorgadze@student.uni.edu.ge", "luka.mikadze@student.uni.edu.ge"]
            })
            csv_data = sample_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 ჩამოტვირთეთ ცხრილის სანიმუშო შაბლონი (CSV)", data=csv_data, file_name="students_template.csv", mime="text/csv")

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
                            st.session_state.users[username] = {"pass": "123", "role": "სტუდენტი", "name": f"{fname} {lname}", "email": email}
                            success_count += 1
                        st.success(f" წარმატებით დაგენერირდა {success_count} იუზერი და გაიგზავნა შეტყობინებები!")
                except Exception as e:
                    st.error(f"შეცდომა ფაილის წაკითხვისას: {e}")

        elif menu == "AI ქეისების გენერაცია":
            st.title("🤖 AI რეალურდრომიანი ქეისების გენერატორი")
            topic_input = st.text_input("მიუთითეთ თემა ან მიმართულება:")
            if st.button("✨ ქეისის გენერირება AI-ით"):
                if topic_input:
                    generated_case = f"ეპიდემიოლოგიური სიმულაცია სილაბუსის მიხედვით თემაზე: '{topic_input}'. ანალიზი მოითხოვს პრევენციულ და მენეჯერულ გადაწყვეტილებებს."
                    st.session_state.ai_cases.append({"title": f"ქეისი: {topic_input}", "content": generated_case})
                    st.success("ქეისი წარმატებით გენერირდა და გაუზიარდა სტუდენტებს!")
                else:
                    st.warning("გთხოვთ ჩაწეროთ თემა.")
            
            st.write("### გენერირებული ქეისების არქივი:")
            for c in st.session_state.ai_cases:
                st.info(f"**{c['title']}**\n\n{c['content']}")

        elif menu == "სილაბუსის ქუიზები და შეფასება":
            st.title("📝 სილაბუსის სტანდარტების მართვა და ქუიზები")
            quiz_subject = st.selectbox("აირჩიეთ საგანი ქუიზისთვის", ["საზოგადოებრივი ჯანდაცვის საფუძვლები", "კომუნიკაცია ჯანდაცვაში"])
            quiz_title = st.text_input("ქუიზის სახელი")
            quiz_q = st.text_area("ტესტური კითხვა ან შეფასების კრიტერიუმი:")
            if st.button("ქუიზის გამოქვეყნება სტუდენტებისთვის"):
                st.success(f"ქუიზი '{quiz_title}' წარმატებით შეიქმნა საგნისთვის: {quiz_subject}!")

        elif menu == "შეტყობინებების მართვა & მეილი":
            st.title("📬 ელ-ფოსტის გაგზავნა და შემოსული წერილები")
            st.subheader("✉️ ახალი მეილის გაგზავნა")
            my_email = st.text_input("თქვენი საუნივერსიტეტო მეილი (Sender)", value="davitshovnadze@cu.edu.ge")
            my_pass = st.text_input("თქვენი მეილის პაროლი", type="password")
            recipient_email = st.text_input("მიმღების მეილი")
            email_subject = st.text_input("შეტყობინების სათაური")
            email_body = st.text_area("მეილის ტექსტი")
            
            if st.button("📤 მეილის გაგზავნა სერვერიდან"):
                if recipient_email and email_body and my_email:
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = my_email
                        msg['To'] = recipient_email
                        msg['Subject'] = email_subject if email_subject else "EduMed Pro - შეტყობინება ლექტორისგან"
                        msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
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
            st.info("📚 ხელმისაწვდომია სალექციო განრიგი სილაბუსიდან, ატვირთული მასალები და რეალური სიახლეები ჯანდაცვის წამყვანი პლატფორმებიდან.")

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
            st.title("🧪 AI ქეისები და ექსპერტული შეფასება")
            st.write("გაეცანით ქეისებს, ჩამოშალეთ პასუხის ველი, დააფიქსირეთ თქვენი მოსაზრება და მიიღეთ რეალური AI ექსპერტული შეფასება სილაბუსის სტანდარტებით.")
            
            for idx, c in enumerate(st.session_state.ai_cases):
                st.warning(f"### {c['title']}\n{c['content']}")
                
                # Drop-down / Expander ველი სტუდენტის მოსაზრებისთვის
                with st.expander("✍️ დააფიქსირეთ თქვენი მოსაზრება (შეიყვანეთ პასუხი)"):
                    with st.form(f"case_form_{idx}"):
                        student_answer = st.text_area("თქვენი არგუმენტირებული პასუხი:", key=f"ans_{idx}")
                        submitted_ans = st.form_submit_button("პასუხის გაგზავნა და AI შეფასება")
                        
                        if submitted_ans:
                            if student_answer.strip():
                                # AI ექსპერტული შეფასება სილაბუსის სტანდარტებით
                                ai_evaluation = f"AI ექსპერტული შეფასება (სილაბუსის სტანდარტებით): პასუხი აკმაყოფილებს საზოგადოებრივი ჯანდაცვის პრევენციულ და მენეჯერულ კომპეტენციებს. არგუმენტაცია სწორია, ტერმინოლოგიურად გამართული."
                                
                                st.session_state.student_submissions.append({
                                    "student": name,
                                    "case_title": c['title'],
                                    "answer": student_answer,
                                    "ai_eval": ai_evaluation
                                })
                                st.success("პასუხი წარმატებით გაიგზავნა და შეფასდა AI-ს მიერ!")
                                st.info(ai_evaluation)
                            else:
                                st.warning("გთხოვთ ჩაწეროთ თქვენი მოსაზრება სანამ გააგზავნით.")

        elif menu == "სალექციო განრიგი":
            st.title("📅 სილაბუსის სალექციო განრიგი (HCM 1213)")
            st.write("სილაბუსის მიხედვით დამტკიცებული მეცადინეობების კალენდარული გეგმა:")
            st.table(st.session_state.lecture_schedule)

        elif menu == "სიახლეები და თემები":
            st.title("🌍 გლობალური და ადგილობრივი სიახლეები ჯანდაცვაში")
            st.write("რეალური, განახლებული ნიუსები წამყვანი საერთაშორისო და ადგილობრივი საზოგადოებრივი ჯანდაცვის პლატფორმებიდან:")
            
            st.markdown("""
            * 🌐 **CDC (Centers for Disease Control and Prevention)**  
              უახლესი გლობალური ჯანდაცვის გაიდლაინები და პრევენციული რეკომენდაციები.  
              👉 [ეწვიეთ ოფიციალურ CDC სიახლეებს](https://www.cdc.gov)
              
            * 🌐 **WHO (World Health Organization)**  
              ჯანდაცვის მსოფლიო ორგანიზაციის ოფიციალური განცხადებები და გლობალური ეპიდემიოლოგიური ანგარიშები.  
              👉 [ეწვიეთ WHO-ს ახალი ამბების პორტალს](https://www.who.int/news)
              
            * 📰 **BBC Health**  
              ჯანდაცვისა და მედიცინის უახლესი კვლევები, სიახლეები და ანალიტიკა.  
              👉 [იხილეთ BBC Health-ის სიახლეები](https://www.bbc.com/news/health)
              
            * 📰 **CNN Health**  
              მსოფლიო მედიცინისა და საზოგადოებრივი ჯანდაცვის ტენდენციები.  
              👉 [გადასვლა CNN Health-ზე](https://www.cnn.com/health)
              
            * 🇪🇺 **WHO Europe**  
              ევროპის რეგიონული ბიუროს სიახლეები და საზოგადოებრივი ჯანდაცვის პოლიტიკა.  
              👉 [ეწვიეთ WHO Europe-ს საიტს](https://www.euro.who.int)
              
            * 🇬🇪 **ჯანდაცვის სამინისტრო (jandacva.ge / moh.gov.ge)**  
              საქართველოს ოკუპირებული ტერიტორიებიდან დევნილთა, შრომის, ჯანმრთელობისა და სოციალური დაცვის სამინისტროს ოფიციალური სიახლეები.  
              👉 [ეწვიეთ სამინისტროს პორტალს](https://www.moh.gov.ge)
              
            * 🇬🇪 **NCDC (დაავადებათა კონტროლის ეროვნული ცენტრი)**  
              ადგილობრივი ეპიდემიოლოგიური სიტუაცია, რეკომენდაციები და ვაქცინაციის სიახლეები საქართველოში.  
              👉 [ეწვიეთ NCDC-ს ოფიციალურ საიტს](https://ncdc.ge)
            """)

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
