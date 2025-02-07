import os
os.environ['KIVY_LOG_LEVEL'] = 'error'
os.environ['KIVY_NO_CONSOLELOG'] = '1'
from tensorflow.keras.models import load_model
model1 = load_model(r"P:\ML\CaptchaDetection\ensembled_models\NEW_ENSEMBLED_MODEL1.keras")
model2 = load_model(r"P:\ML\CaptchaDetection\ensembled_models\NEW_ENSEMBLED_MODEL2.keras")
model3 = load_model(r"P:\ML\CaptchaDetection\ensembled_models\NEW_ENSEMBLED_MODEL3.keras")
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDRoundFlatButton
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.core.clipboard import Clipboard
import threading
import numpy as np
import cv2
class CaptchaSolver():
    def __init__(self, models):
        self.model1 = models[0]
        self.model2 = models[1]
        self.model3 = models[2]
    def extract(self, image_path):
        predictions = self.ensemble_predict(image_path)
        out = ''
        for j in predictions:
            out += ''.join(["abcdefghijklmnopqrstuvwxyz0123456789"[i] for i in j])
        print("Output: ", out)
        return out

    def ensemble_predict(self, image_path):
        models = [self.model1, self.model2, self.model3]
        resized_scale = (56, 56, 1)
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)[:, 20:-50]
        _, binary = cv2.threshold(img, 40, 250, cv2.THRESH_BINARY_INV)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        after = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        width = img.shape[1] // 5
        ensemble_pred = []
        for i in range(5):
            predictions = []
            
            char_img = after[:, i * width:(i + 1) * width]
            char_img = cv2.resize(char_img, resized_scale[:-1])
            char_img = np.expand_dims(char_img, axis=-1)
            char_img = np.expand_dims(char_img, axis=0)
            for model in models:
                predictions.append(model.predict(char_img, verbose=0))
                
            predictions = np.array(predictions)
            ensemble_pred.append(np.argmax(np.mean(predictions, axis=0), axis=1))

        return ensemble_pred

Window.set_icon("icon.png")
Window.size = (400, 650)

KV = '''
#:import os os
#:import Window kivy.core.window.Window
#:import HoverCard __main__.HoverCard

<HoverCard>:
    elevation: 6
    md_bg_color: [1, 1, 1, 0.8]
    padding: "8dp"
    size_hint: None, None
    size: min(Window.width * 0.9, Window.height * 0.6), min(Window.width * 0.9, Window.height * 0.6)
    pos_hint: {"center_x": 0.5}
    on_enter: self.elevation = 30
    on_leave: self.elevation = 6

<FilePopupContent@BoxLayout>:
    orientation: 'vertical'
    spacing: "10dp"
    padding: "10dp"

    MDTopAppBar:
        id: toolbar
        title: "[b]{}[/b]".format(os.path.basename(file_chooser.path))
        left_action_items: [["arrow-left", lambda x: app.navigate_up(file_chooser)]]
        right_action_items: [["home", lambda x: setattr(file_chooser, 'path', os.path.expanduser('~'))]]
        md_bg_color: app.theme_cls.primary_color
        specific_text_color: 1, 1, 1, 1
        elevation: 4
        size_hint_y: None
        height: "48dp"

    RelativeLayout:
        FileChooserIconView:
            id: file_chooser
            filters: ["*.png", "*.jpg", "*.jpeg"]
            path: os.path.expanduser("~")
            size_hint: 1, 1
            pos_hint: {'top': 1, 'x': 0}
            icon_size: "48dp"
            preview: True
            multiselect: False
            dirselect: False
            on_selection: select_btn.disabled = not self.selection

    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        height: "60dp"
        spacing: "20dp"
        padding: "10dp"

        MDRaisedButton:
            id: select_btn
            text: "SELECT"
            icon: "check-circle"
            md_bg_color: app.theme_cls.accent_color
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            disabled: True
            size_hint_x: 0.5
            on_release: app.select_image(file_chooser.selection)

        MDFlatButton:
            text: "CANCEL"
            icon: "close-circle"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color
            size_hint_x: 0.5
            on_release: app.popup.dismiss()

BoxLayout:
    orientation: 'vertical'
    canvas.before:
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'bg.jpeg'
        Color:
            rgba: [0.1, 0.1, 0.1, 0.3]
        Rectangle:
            pos: self.pos
            size: self.size

    MDTopAppBar:
        title: "CAPTCHA Solver"
        elevation: 4
        left_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]
        right_action_items: [["information-outline", lambda x: app.show_info()]]
        md_bg_color: app.theme_cls.primary_color

    ScrollView:
        id: scroll
        effect_cls: "ScrollEffect"
        scroll_type: ['bars', 'content']
        bar_width: "6dp"

        BoxLayout:
            orientation: 'vertical'
            spacing: "20dp"
            padding: "20dp"
            size_hint_y: None
            height: self.minimum_height

            HoverCard:
                id: image_card
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: "10dp"

                    RelativeLayout:
                        MDRaisedButton:
                            opacity: 0
                            size_hint: 0.95, 0.95
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            on_release: app.show_full_image()
                        FitImage:
                            id: captcha_image
                            source: ''
                            size_hint: 0.95, 0.95
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            allow_stretch: True
                            keep_ratio: False
                            radius: image_card.radius
                            opacity: 0.4

                        MDLabel:
                            id: solved_label
                            text: ""
                            halign: "center"
                            valign: "center"
                            font_style: "H5"
                            bold: True
                            theme_text_color: "Custom"
                            text_color: "white"
                            size_hint: 0.6, 0.2
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                            opacity: 0
                            md_bg_color: (50/255, 168/255, 125/255)
                            radius: [self.height/2,]
                            padding: "10dp"

                    MDBoxLayout:
                        id: progress_box
                        orientation: 'vertical'
                        size_hint_y: 0.15
                        spacing: "10dp"
                        padding: "10dp"

                        MDLabel:
                            id: status_label
                            text: "Upload a CAPTCHA image to begin"
                            halign: "center"
                            bold: True
                            font: "ARIAL.ttf"
                            font_style: "Subtitle1"
                            theme_text_color: "Custom"
                            text_color: app.theme_cls.primary_color 
                            opacity: 1

                        MDProgressBar:
                            id: progress_bar
                            value: 0
                            max: 2
                            opacity: 1

            BoxLayout:
                orientation: 'vertical'
                spacing: "15dp"
                size_hint_y: None
                height: self.minimum_height

                MDRoundFlatButton:
                    id: upload_btn
                    text: "UPLOAD IMAGE"
                    icon: "cloud-upload"
                    font_size: "18sp"
                    pos_hint: {"center_x": 0.5}
                    on_release: app.open_file_chooser()
                    md_bg_color: app.theme_cls.primary_color
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1

                MDRoundFlatButton:
                    id: solve_button
                    text: "SOLVE CAPTCHA"
                    icon: "auto-fix"
                    font_size: "18sp"
                    pos_hint: {"center_x": 0.5}
                    on_release: app.extract()
                    disabled: True
                    md_bg_color: app.theme_cls.primary_color
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1

                MDFloatingActionButton:
                    id: save_btn
                    icon: "content-save"
                    pos_hint: {"center_x": 0.5}
                    elevation: 0
                    opacity: 0
                    on_release: app.to_clipboard()
                    md_bg_color: app.theme_cls.primary_color
'''

class HoverCard(MDCard):
    radius = ListProperty([20, 20, 20, 20])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_radius)

    def update_radius(self, *args):
        base_radius = self.height * 0.05
        self.radius = [base_radius] * 4
solver = CaptchaSolver((model1, model2, model3))
class CaptchaSolverApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def build(self):
        self.title = "CAPTCHA Solver Pro"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.theme_style = "Dark"
        self.file_path = None
        self.popup = None
        return Builder.load_string(KV)

    def toggle_theme(self):
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"
        else:
            self.theme_cls.theme_style = "Dark"

    def show_info(self):
        self.info_dialog = MDDialog(
            title="CAPTCHA Solver Guide",
            text="1. Click UPLOAD IMAGE to select a CAPTCHA image\n2. Click SOLVE CAPTCHA to extract text\n3. Save the result using save button",
            radius=[20, 20, 20, 20],
            buttons=[
                MDRoundFlatButton(
                    text="GOT IT",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=lambda x: self.info_dialog.dismiss()
                )
            ],
        )
        self.info_dialog.open()

    def open_file_chooser(self):
        content = Builder.load_string('''
FilePopupContent:
    size_hint: 1, 1
''')
        self.popup = Popup(
            title='',
            content=content,
            size_hint=(0.95, 0.8),
            separator_color=self.theme_cls.primary_color,
            background_color=(1,1,0,1),
            overlay_color=(0, 0, 0, 0.4),
            auto_dismiss=True
        )
        self.popup.open()

    def navigate_up(self, file_chooser):
        current_path = file_chooser.path
        parent_path = os.path.dirname(current_path)
        if os.path.exists(parent_path):
            file_chooser.path = parent_path

    def select_image(self, selection):
        self.root.ids.progress_bar.value = 0
        if selection:
            self.file_path = selection[0]
            self.root.ids.captcha_image.source = self.file_path
            self.root.ids.solve_button.disabled = False
            self.root.ids.status_label.text = "Image uploaded successfully!"
            self.animate_image_upload()
            self.popup.dismiss()

    def animate_image_upload(self):
        image_anim = Animation(opacity=1, duration=0.5) + Animation(size_hint_y=0.95)
        image_anim.start(self.root.ids.captcha_image)
        
        card = self.root.ids.image_card
        target_width = card.width * 1.2
        target_height = card.height//1.5
        card_anim = Animation(size=(target_width, target_height), duration=0.5)
        card_anim.start(card)
        
        Animation(opacity=1, duration=0.3).start(self.root.ids.status_label)
        Clock.schedule_once(lambda dt: Animation(opacity=0, duration=1).start(self.root.ids.status_label), 2)
    def extract(self):
        if self.file_path:
            try:
                self.root.ids.solve_button.disabled = True
                self.root.ids.status_label.text = "Extracting Text..."
                self.root.ids.status_label.opacity = 1
                self.root.ids.progress_bar.value = 1
                threading.Thread(target=self.run_captcha_extraction).start()
            except:
                self.root.ids.status_label.text = "Error"
                Clock.schedule_once(lambda dt: setattr(self.root.ids.status_label, 'opacity', 0), 2)

    def run_captcha_extraction(self):
        try:
            detected_text = solver.extract(self.file_path)
            Clock.schedule_once(lambda dt: self.update_captcha_result(detected_text))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_extraction_error(str(e)))

    def update_captcha_result(self, text):
        self.root.ids.progress_bar.value = 2
        self.root.ids.status_label.text = f"Extracted Text: {text}"
        self.root.ids.status_label.opacity = 1
        self.root.ids.solved_label.text = "Text Extracted!"
        anim = Animation(opacity=1, duration=0.5) + Animation(opacity=1, duration=1.5) + Animation(opacity=0, duration=0.5)
        anim.start(self.root.ids.solved_label)
        self.root.ids.solve_button.disabled = False
        Animation(opacity=1, d=0.5).start(self.root.ids.save_btn)

    def show_extraction_error(self, error):
        self.root.ids.status_label.text = f"Error: {error}"
        self.root.ids.progress_bar.value = 0
        self.root.ids.solve_button.disabled = False

    def to_clipboard(self):
        #
        extracted_text = self.root.ids.status_label.text.replace("Extracted Text: ", "")
        Clipboard.copy(extracted_text)
        self.root.ids.status_label.text = "Result copied to clipboard!"
        self.root.ids.solved_label.text = "Copied!"
        anim = Animation(opacity=1, duration=0.5) + Animation(opacity=1, duration=1.5) + Animation(opacity=0, duration=0.5)
        anim.start(self.root.ids.solved_label)
        self.root.ids.status_label.opacity = 0
        Animation(opacity=1, d=0.5).start(self.root.ids.save_btn)

    def show_full_image(self):
        if not self.root.ids.captcha_image.source:
            return
        
        content = FloatLayout()
        img = AsyncImage(
            source=self.root.ids.captcha_image.source,  
            keep_ratio=True,
            allow_stretch=True,
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.55}
        )
        bt = MDRaisedButton(
            text="Close",
            theme_text_color="Custom",
            md_bg_color=self.theme_cls.accent_color,
            text_color=(1, 1, 1, 1),
            size_hint=(0.3, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            on_release=lambda x: self.image_popup.dismiss()
        )
        content.add_widget(img)
        content.add_widget(bt)

        self.image_popup = Popup(
            title='Full View',
            content=content,
            size_hint=(0.5, 0.5),
            separator_color=self.theme_cls.primary_color,
            background_color=(0.5,0.2,0.3,1),
            overlay_color=(0, 0, 0, 0.5),
            title_color=self.theme_cls.primary_color
        )
        self.image_popup.open()

if __name__ == "__main__":
    CaptchaSolverApp().run()