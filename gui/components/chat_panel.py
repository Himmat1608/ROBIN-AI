import customtkinter as ctk

class ChatPanel(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        # Override hardcoded aesthetics from app.py to enforce design system
        kwargs["fg_color"] = "#0A0A0A"
        if "border_width" in kwargs:
            kwargs.pop("border_width")
            
        super().__init__(master, **kwargs)

    def append_message(self, sender: str, text: str):
        is_user = sender.upper() != "ROBIN"
        
        # Message bubble container (invisible padding row)
        msg_container = ctk.CTkFrame(self, fg_color="transparent")
        msg_container.pack(fill="x", pady=3, padx=10) # 6px total gap between bubbles
        
        # Bubble styling
        bubble_bg = "#1A1A2E" if is_user else "#111111"
        text_color = "#00FFCC" if is_user else "#D6D6D6"
        
        bubble = ctk.CTkFrame(msg_container, fg_color=bubble_bg, corner_radius=16)
        bubble.pack(side="right" if is_user else "left")
        
        # Text block
        lbl = ctk.CTkLabel(
            bubble,
            text=text,
            text_color=text_color,
            font=ctk.CTkFont(family="Inter", size=13, weight="normal"),
            justify="left",
            wraplength=220 # Approx 70-75% max width for standard window geometry
        )
        lbl.pack(padx=12, pady=8) # Internal padding
        
        # Auto scroll to bottom smoothly
        self.update_idletasks()
        try:
            self._parent_canvas.yview_moveto(1.0)
        except AttributeError:
            pass