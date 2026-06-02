import customtkinter as ctk

class InputPanel(ctk.CTkFrame):
    def __init__(self, master, on_send_callback, **kwargs):
        # Override container background to blend with chat panel
        kwargs["fg_color"] = "transparent"
        super().__init__(master, **kwargs)
        
        self.on_send_callback = on_send_callback
        
        # Premium input field
        self.input_field = ctk.CTkEntry(
            self, 
            placeholder_text="Message Robin...", 
            placeholder_text_color="#555555",
            text_color="#FFFFFF",
            fg_color="#111111",
            border_color="#222222",
            border_width=1,
            corner_radius=20,
            height=42,
            font=ctk.CTkFont(family="Inter", size=13, weight="normal")
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(10, 8), pady=5)
        self.input_field.bind("<Return>", self._on_enter_pressed)
        
        # Compact, pill-shaped send button
        self.send_btn = ctk.CTkButton(
            self, 
            text="↑", 
            width=36, 
            height=36,
            fg_color="#00FFCC",
            text_color="#000000",
            hover_color="#33FFD6",
            corner_radius=18,
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            command=self._handle_send
        )
        self.send_btn.pack(side="right", padx=(0, 10), pady=5)
        
    def _on_enter_pressed(self, event):
        self._handle_send()
        
    def _handle_send(self):
        text = self.input_field.get().strip()
        if text:
            self.input_field.delete(0, "end")
            self.on_send_callback(text)
