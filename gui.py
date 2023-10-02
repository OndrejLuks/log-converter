import customtkinter

class CheckboxFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.checkbox_1 = customtkinter.CTkSwitch(self, text="Option 1")
        self.checkbox_1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.checkbox_2 = customtkinter.CTkSwitch(self, text="Option 2")
        self.checkbox_2.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.checkbox_3 = customtkinter.CTkSwitch(self, text="Option 3")
        self.checkbox_3.grid(row=2, column=0, padx=10, pady=10, sticky="w")


    def get(self):
        result = []
        if self.checkbox_1.get() == 1:
            result.append("Yolo [1] selected")
        if self.checkbox_2.get() == 1:
            result.append("Yolo [2] selected")
        if self.checkbox_3.get() == 1:
            result.append("Yolo [3] selected")
        return result


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simple test")
        self.geometry("400x200")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.checkbox_frame = CheckboxFrame(self)
        self.checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")

        self.btn = customtkinter.CTkButton(self, text="Click me!", command=self.btn_callback)
        self.btn.grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky="ew")


    def btn_callback(self):
        print("Oi, selected: ", self.checkbox_frame.get())


app = App()
app.mainloop()