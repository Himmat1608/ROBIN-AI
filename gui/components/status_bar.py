import customtkinter as ctk

class StatusBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs["fg_color"] = "transparent"
        kwargs["height"] = 30
        kwargs["corner_radius"] = 0
        super().__init__(master, **kwargs)
        
        self.current_raw_status = "idle"
        
        # Ambient centering
        self.status_container = ctk.CTkFrame(self, fg_color="transparent")
        self.status_container.pack(expand=True, pady=10)
        
        # 8px rounded dot
        self.dot = ctk.CTkFrame(self.status_container, width=8, height=8, corner_radius=4, fg_color="#444444")
        self.dot.pack(side="left", padx=(0, 6))
        self.dot.pack_propagate(False)
        
        # Subtle lowercase status text
        self.status_label = ctk.CTkLabel(
            self.status_container, 
            text="idle", 
            text_color="#666666", 
            font=ctk.CTkFont(family="Inter", size=11, weight="normal")
        )
        self.status_label.pack(side="left")

    def set_status(self, status: str, color: str = None):
        self.current_raw_status = status.lower()
        
        display_text = self.current_raw_status
        target_color = "#444444"
        text_color = "#666666"
        
        if "listening" in display_text:
            display_text = "listening"
            target_color = "#00FF88"
            text_color = "#A0A0A0"
        elif "speaking" in display_text:
            display_text = "speaking"
            target_color = "#C084FC"
            text_color = "#A0A0A0"
        elif "thinking" in display_text:
            display_text = "thinking"
            target_color = "#FFD166"
            text_color = "#A0A0A0"
        elif "active" in display_text or "idle" in display_text or "ready" in display_text:
            display_text = "active"
            target_color = "#5C7A8A"
            text_color = "#666666"
            
        self.status_label.configure(text=display_text, text_color=text_color)
        
        # Initiate soft fade over 150ms
        current_color = self.dot.cget("fg_color")
        if isinstance(current_color, list):
            current_color = current_color[0]
        self._fade_dot(current_color, target_color, steps=5)

    def _fade_dot(self, current_hex, target_hex, steps, current_step=0):
        if current_step >= steps or current_hex == target_hex or current_hex == "transparent":
            self.dot.configure(fg_color=target_hex)
            return
            
        try:
            c_r, c_g, c_b = int(current_hex[1:3], 16), int(current_hex[3:5], 16), int(current_hex[5:7], 16)
            t_r, t_g, t_b = int(target_hex[1:3], 16), int(target_hex[3:5], 16), int(target_hex[5:7], 16)
            
            n_r = int(c_r + (t_r - c_r) * (current_step / steps))
            n_g = int(c_g + (t_g - c_g) * (current_step / steps))
            n_b = int(c_b + (t_b - c_b) * (current_step / steps))
            
            self.dot.configure(fg_color=f"#{n_r:02x}{n_g:02x}{n_b:02x}")
            self.after(30, self._fade_dot, current_hex, target_hex, steps, current_step + 1)
        except Exception:
            self.dot.configure(fg_color=target_hex)

    def get_status(self) -> str:
        return getattr(self, "current_raw_status", "")
