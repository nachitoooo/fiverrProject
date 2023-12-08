import tkinter as tk
from PIL import Image, ImageTk
class RoundedFrame(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.config(bg='#06061f', highlightbackground="lightgrey", highlightthickness=2)
        self.create_rounded_frame()

    def create_rounded_frame(self):
        square_size = 200  # Ajusta el tamaño según sea necesario
        rounded_image = Image.new("RGBA", (square_size, square_size), "#06061f")
        mask = Image.new("L", (square_size, square_size), 0)
        mask.paste(rounded_image, (0, 0), rounded_image)
        rounded_frame = Image.new("RGBA", (square_size, square_size), "#06061f")
        rounded_frame.paste(rounded_image, (0, 0), mask)
        self.rounded_frame_tk = ImageTk.PhotoImage(rounded_frame)

        self.create_image(0, 0, anchor=tk.NW, image=self.rounded_frame_tk)