# Early frontend prototype
# Created during the initial phase of the hackathon
# This is NOT the final frontend implementation
# Final frontend was developed separately by the frontend team member

import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock 
from kivy.uix.spinner import Spinner

API_BASE = "https://not-quite-prototype-3.onrender.com"

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.username = TextInput(hint_text="Username")
        self.password = TextInput(hint_text="Password", password=True)
        self.box.add_widget(Label(text="Login"))
        self.box.add_widget(self.username)
        self.box.add_widget(self.password)
        self.box.add_widget(Button(text="Log in", on_press=self.login))
        self.box.add_widget(Button(text="Signup", on_press=self.goto_signup))
        self.add_widget(self.box)

    def login(self, instance):
        # Dummy login, implement API logic if needed
        self.manager.current = "dashboard"

    def goto_signup(self, instance):
        self.manager.current = "signup"

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.name_input = TextInput(hint_text="Name")
        self.email_input = TextInput(hint_text="Email")
        self.password_input = TextInput(hint_text="Password", password=True)
        self.dob = TextInput(hint_text="Date of Birth")
        self.box.add_widget(Label(text="Create Account"))
        self.box.add_widget(self.name_input)
        self.box.add_widget(self.email_input)
        self.box.add_widget(self.password_input)
        self.box.add_widget(self.dob)
        self.box.add_widget(Button(text="Signup", on_press=self.signup))
        self.box.add_widget(Button(text="Already Registered? Log in", on_press=self.goto_login))
        self.add_widget(self.box)

    def signup(self, instance):
        # Dummy signup, implement API if needed
        popup = Popup(title='Account Created', content=Label(text='Success!'), size_hint=(None, None), size=(300, 200))
        popup.open()

    def goto_login(self, instance):
        self.manager.current = "login"

class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.box.add_widget(Label(text="Dashboard"))
        self.box.add_widget(Button(text="Take Quiz", on_press=self.goto_quiz))
        self.box.add_widget(Button(text="Emergency Messages", on_press=self.goto_emergency))
        self.box.add_widget(Button(text="Profile", on_press=self.goto_profile))
        self.add_widget(self.box)

    def goto_quiz(self, instance):
        self.manager.get_screen("quiz").load_quiz()
        self.manager.current = "quiz"
    
    def goto_emergency(self, instance):
        self.manager.current = "emergency"


    def goto_profile(self, instance):
        self.manager.get_screen("profile").load_progress()
        self.manager.current = "profile"

class QuizScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.q_label = Label(text="Quiz will appear here")
        self.hint_label = Label(text="")
        self.option_inputs = [Button(text="", on_press=self.submit_answer) for _ in range(4)]
        self.box.add_widget(self.q_label)
        self.box.add_widget(self.hint_label)
        for btn in self.option_inputs:
            self.box.add_widget(btn)
        controls = BoxLayout(size_hint_y=None, height=50)
        self.reset_btn = Button(text="Reset", on_press=self.reset_quiz)
        self.restart_btn = Button(text="Restart", on_press=self.restart_quiz)
        self.quit_btn = Button(text="Quit", on_press=self.quit_quiz)
        self.next_btn = Button(text="Next", on_press=self.next_question)
        self.progress_btn = Button(text="Progress", on_press=self.show_progress)
        for btn in [self.reset_btn, self.restart_btn, self.quit_btn, self.next_btn, self.progress_btn]:
            controls.add_widget(btn)
        self.box.add_widget(controls)
        self.add_widget(self.box)

        self.questions = []
        self.current_idx = 0
        self.score = 0
        self.current_question = None
        self.answered = False

    def load_quiz(self):
        res = requests.get(f"{API_BASE}/quiz_questions?level=Basic")
        data = res.json()
        if data:
            self.questions = data
            self.current_idx = 0
            self.score = 0
            self.show_current_question()
        else:
            self.q_label.text = "No quiz available."
            self.hint_label.text = ""
            for btn in self.option_inputs:
                btn.text = ""
            self.current_question = None

    def show_current_question(self):
        if self.current_idx < len(self.questions):
            self.current_question = self.questions[self.current_idx]
            self.q_label.text = self.current_question.get('Question', 'No question')
            self.hint_label.text = ""
            for idx, opt in enumerate(['A', 'B', 'C', 'D']):
                self.option_inputs[idx].background_color = [1, 1, 1, 1]
                self.option_inputs[idx].text = f"{opt}: {self.current_question['Options'][idx]}"
            self.answered = False
        else:
            self.current_question = None
            self.q_label.text = "Quiz finished!"
            self.hint_label.text = ""

    def submit_answer(self, instance):
        if self.current_question is None or self.answered:
            return
        selected = instance.text.split(":")[0]
        correct_letter = None
        for idx, opt_letter in enumerate(['A', 'B', 'C', 'D']):
            if self.current_question['Options'][idx] == self.current_question['Answer']:
                correct_letter = opt_letter
                break
        if selected == correct_letter:
            self.hint_label.text = ""
            self.q_label.text = "Correct!"
            instance.background_color = [0, 1, 0, 1]
            self.score += 1
            self.answered = True
            Clock.schedule_once(lambda dt: self.next_question(), 1)
        else:
            self.q_label.text = self.current_question.get('Question', 'No question')
            self.hint_label.text = f"Hint: {self.current_question.get('Hint', '')}"
            instance.background_color = [1, 0, 0, 1]
            self.answered = True

    def next_question(self, instance=None):
        if self.current_idx < len(self.questions) - 1:
            self.current_idx += 1
            self.show_current_question()
        else:
            self.current_question = None
            popup = Popup(title='Finished', content=Label(text=f'Quiz finished!\nScore: {self.score}/{len(self.questions)}'), size_hint=(0.5, 0.5))
            popup.open()

    def reset_quiz(self, instance):
        self.show_current_question()
        self.score = 0

    def restart_quiz(self, instance):
        self.current_idx = 0
        self.score = 0
        self.show_current_question()

    def quit_quiz(self, instance):
        self.manager.current = "dashboard"

    def show_progress(self, instance):
        popup = Popup(title='Progress', content=Label(text=f'Current Score: {self.score}\nQuestion: {self.current_idx + 1} / {len(self.questions)}'), size_hint=(0.5, 0.5))
        popup.open()

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical', padding=20, spacing=15)

        self.title_label = Label(
            text="[b]User Profile[/b]",
            markup=True,
            font_size="24sp",
            size_hint_y=None,
            height=40
        )
        self.profile_name = Label(
            text="User ID: ",
            font_size="18sp"
        )
        self.profile_quizzes = Label(
            text="Quizzes Completed: ",
            font_size="18sp"
        )
        self.profile_avg = Label(
            text="Average Score: ",
            font_size="18sp"
        )
        self.back_btn = Button(
            text="Back to Dashboard",
            size_hint_y=None,
            height=40,
            on_release=self.back_to_dashboard
        )

        self.box.add_widget(self.title_label)
        self.box.add_widget(self.profile_name)
        self.box.add_widget(self.profile_quizzes)
        self.box.add_widget(self.profile_avg)
        self.box.add_widget(self.back_btn)
        self.add_widget(self.box)

    def load_progress(self):
        res = requests.get(f"{API_BASE}/progress?user_id=testuser")
        data = res.json()
        self.profile_name.text = f"User ID: {data.get('user_id', 'Unknown')}"
        self.profile_quizzes.text = f"Quizzes Completed: {data.get('progress', {}).get('quizzes_completed', 0)}"
        self.profile_avg.text = f"Average Score: {data.get('progress', {}).get('average_score', 0)}"

    def back_to_dashboard(self, instance):
        self.manager.current = "dashboard"

class EmergencyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.box = BoxLayout(orientation='vertical')
        self.disasters = ['Earthquake', 'Fire', 'Flood', 'Cyclone', 'Cyber Attack']
        self.spinner = Spinner(text='Select Disaster', values=self.disasters, size_hint=(1, None), height=44)
        self.box.add_widget(self.spinner)
        self.show_btn = Button(text="View Messages")
        
        #type: ignore
        #self.show_btn.bind(on_press=self.show_messages)

        self.show_btn.bind(on_press=self.show_messages)
        self.box.add_widget(self.show_btn)
        back_btn = Button(text='Back', size_hint=(1, None), height=44)
        back_btn.bind(on_press=self.go_back)
        self.box.add_widget(back_btn)

        self.msg_label = Label(text="")
        self.box.add_widget(self.msg_label)
        self.add_widget(self.box)
    
    def go_back(self, instance):
        self.manager.current = 'dashboard'

    def show_messages(self, instance):
        disaster = self.spinner.text.strip()
        try:
            response = requests.get(f"{API_BASE}/emergency_messages?disaster={disaster}")
            data = response.json()

            if not data or data == {}:
                self.msg_label.text = f"No {disaster} messages found"
                return

            parts = []
            for section in ['warnings', 'alerts', 'safety_protocols', 'advice']:
                if data.get(section):
                   items = "\n".join(f"- {item}" for item in data[section])
                   parts.append(f"{section.capitalize()}:\n{items}")
            self.msg_label.text = "\n\n".join(parts) if parts else f"No messages for {disaster}"

        except Exception as e:
            self.msg_label.text = f"Error: {str(e)}"

class DisasterApp(App):
    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(SignupScreen(name="signup"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(QuizScreen(name="quiz"))
        self.sm.add_widget(ProfileScreen(name="profile"))
        self.sm.add_widget(EmergencyScreen(name="emergency"))
        return self.sm

if __name__ == "__main__":
    DisasterApp().run()

