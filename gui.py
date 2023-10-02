import customtkinter

class TrueFalseFrame(customtkinter.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.switches = []

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="orange", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            switch = customtkinter.CTkSwitch(self, text=value)
            switch.grid(row=i+1, column=0, padx=10, pady=5, sticky="w")
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


        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.checkbox_frame = TrueFalseFrame(self, title="Select T/F:", values=["Option 1", "Option 2", "Option 3", "Option 4"])
        self.checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nswe")
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Tu zadaj text...")
        self.entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.textbox = customtkinter.CTkTextbox(master=self)
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

        self.btn = customtkinter.CTkButton(self, text="Click me!", command=self.btn_callback)
        self.btn.grid(row=2, column=0, padx=10, pady=10, columnspan=2, sticky="ew")


    def btn_callback(self):
        self.textbox.insert("end", f"You just inserted:\n{self.entry.get()}\n")
        self.textbox.see("end")
        print("Oi, selected: ", self.checkbox_frame.get())


app = App()
app.mainloop()