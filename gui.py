import customtkinter

class TrueFalseFrame(customtkinter.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)
        self.values = values
        self.switches = []

        for i, value in enumerate(self.values):
            switch = customtkinter.CTkSwitch(self, text=value)
            switch.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            self.switches.append(switch)

    def get(self):
        result = []
        for switch in self.switches:
            result.append(switch.get())
        return result


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simple test")
        self.geometry("400x200")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.checkbox_frame = TrueFalseFrame(self, values=["Option 1", "Option 2", "Option 3", "Option 4"])
        self.checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")

        self.btn = customtkinter.CTkButton(self, text="Click me!", command=self.btn_callback)
        self.btn.grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky="ew")


    def btn_callback(self):
        print("Oi, selected: ", self.checkbox_frame.get())


app = App()
app.mainloop()