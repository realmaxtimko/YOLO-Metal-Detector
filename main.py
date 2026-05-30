import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading

class YoloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Метал Детектор")
        self.root.geometry("1100x750")
        self.root.configure(bg="#1e1e1e")

        self.cv_image = None
        self.camera_running = False
        self.cap = None

        # ==================== МОДЕЛЬ ====================
        try:
            self.model = YOLO("best.pt")
        except Exception as e:
            messagebox.showerror(
                "Помилка",
                f"Не вдалося завантажити модель best6.pt\n\n{e}"
            )
            self.root.destroy()
            return

        # ==================== HEADER ====================
        header = tk.Frame(root, bg="#111111", height=80)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="YOLO РОЗПІЗНАВАННЯ МЕТАЛІВ",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#111111"
        )
        title.pack(pady=20)

        # ==================== CONTROL PANEL ====================
        control_frame = tk.Frame(root, bg="#1e1e1e")
        control_frame.pack(pady=15)

        self.btn_load = tk.Button(
            control_frame,
            text="Завантажити фото",
            command=self.load_image,
            font=("Arial", 13, "bold"),
            bg="#2196F3",
            fg="white",
            width=20,
            height=2,
            bd=0,
            cursor="hand2"
        )
        self.btn_load.grid(row=0, column=0, padx=10)

        self.btn_camera = tk.Button(
            control_frame,
            text="Запустити камеру",
            command=self.toggle_camera,
            font=("Arial", 13, "bold"),
            bg="#FF9800",
            fg="white",
            width=20,
            height=2,
            bd=0,
            cursor="hand2"
        )
        self.btn_camera.grid(row=0, column=1, padx=10)

        self.btn_detect = tk.Button(
            control_frame,
            text="Розпізнати",
            command=self.run_detection,
            font=("Arial", 13, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            bd=0,
            cursor="hand2"
        )
        self.btn_detect.grid(row=0, column=2, padx=10)


        # ==================== IMAGE AREA ====================
        image_frame = tk.Frame(
            root,
            bg="#2d2d2d",
            bd=3,
            relief="ridge"
        )
        image_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.lbl_image = tk.Label(
            image_frame,
            text="Тут буде зображення",
            font=("Arial", 18),
            fg="white",
            bg="#2d2d2d"
        )
        self.lbl_image.pack(expand=True)

    # ==================== LOAD IMAGE ====================
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )

        if file_path:
            image = cv2.imread(file_path)

            if image is None:
                messagebox.showerror("Помилка", "Не вдалося відкрити фото")
                return

            self.cv_image = image
            self.display_image(self.cv_image)

    # ==================== DETECTION ====================
    def run_detection(self):
        if self.cv_image is None:
            messagebox.showwarning(
                "Увага",
                "Спочатку завантажте фото або запустіть камеру"
            )
            return

        results = self.model.predict(
            source=self.cv_image,
            conf=0.5
        )

        for r in results:
            result_img = r.plot()
            self.display_image(result_img)

    # ==================== CAMERA ====================
    def toggle_camera(self):

        if not self.camera_running:
            self.camera_running = True
            self.btn_camera.config(
                text="Зупинити камеру",
                bg="#f44336"
            )

            self.cap = cv2.VideoCapture(0)

            thread = threading.Thread(target=self.update_camera)
            thread.daemon = True
            thread.start()

        else:
            self.camera_running = False

            self.btn_camera.config(
                text="Запустити камеру",
                bg="#FF9800"
            )

            if self.cap:
                self.cap.release()

    def update_camera(self):

        while self.camera_running:

            ret, frame = self.cap.read()

            if ret:
                self.cv_image = frame.copy()

                results = self.model.predict(
                    source=frame,
                    conf=0.5,
                    verbose=False
                )

                for r in results:
                    frame = r.plot()

                self.display_image(frame)

    # ==================== DISPLAY IMAGE ====================
    def display_image(self, cv_img):

        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

        pil_image = Image.fromarray(rgb_image)

        # Масштабування
        width = 900
        height = 550

        pil_image.thumbnail((width, height))

        imgtk = ImageTk.PhotoImage(image=pil_image)

        self.lbl_image.imgtk = imgtk
        self.lbl_image.configure(image=imgtk, text="")


# ==================== START APP ====================
if __name__ == "__main__":

    root = tk.Tk()

    app = YoloApp(root)

    root.mainloop()