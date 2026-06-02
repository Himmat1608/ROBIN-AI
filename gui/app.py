import customtkinter as ctk
import threading
import time
import sys
from core.assistant import RobinAssistant
from voice.listener import listen
from voice.speech_manager import speech_manager, speak
from gui.components.chat_panel import ChatPanel
from gui.components.status_bar import StatusBar
from gui.components.input_panel import InputPanel
from system.monitor import SystemMonitor
from utils.logger import get_logger

logger = get_logger(__name__)


class RobinApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ROBIN")
        self.geometry("350x550")
        self.minsize(300, 450)
        ctk.set_appearance_mode("dark")

        self.assistant = RobinAssistant()
        self.assistant.on_shutdown = lambda: self.after(0, self._on_closing)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.listener_active = False
        self.last_listener_activity = time.time()
        self._listener_thread = None
        self._watchdog_thread = None

        self._build_ui()
        self._setup_callbacks()

        self.chat_panel.append_message("ROBIN", "System Online. Ready.")
        speak("System online. Ready.")

        self.after(4000, self.start_background_listening)
        logger.info("Listener scheduled to start in 4 seconds.")

    def _build_ui(self):
        BG_COLOR = "#0B0F19"
        self.main_container = ctk.CTkFrame(
            self, fg_color=BG_COLOR, corner_radius=0)
        self.main_container.pack(fill="both", expand=True)

        self.status_bar = StatusBar(self.main_container)
        self.status_bar.pack(side="top", fill="x")

        self.info_panel = ctk.CTkFrame(
            self.main_container, fg_color="transparent", height=20)
        self.info_panel.pack(fill="x", padx=10, pady=(5, 0))

        self.cpu_label = ctk.CTkLabel(
            self.info_panel, text="CPU: --%", text_color="#555555")
        self.cpu_label.pack(side="left", padx=5)

        self.ram_label = ctk.CTkLabel(
            self.info_panel, text="RAM: --%", text_color="#555555")
        self.ram_label.pack(side="left", padx=5)

        self.chat_panel = ChatPanel(
            self.main_container, border_width=0,
            fg_color="#151A28", corner_radius=15)
        self.chat_panel.pack(padx=10, pady=10, fill="both", expand=True)

        self.input_panel = InputPanel(
            self.main_container,
            on_send_callback=lambda text: self._process_and_respond(
                text, is_voice=False))
        self.input_panel.pack(padx=10, pady=(0, 15), fill="x")

        self._update_stats()

    def _update_stats(self):
        try:
            status = SystemMonitor.get_system_status()
            if "CPU" in status:
                cpu = status.split("CPU is at ")[1].split(" percent")[0]
                ram = status.split("Memory is at ")[1].split(" percent")[0]
                self.cpu_label.configure(text=f"CPU: {cpu}%")
                self.ram_label.configure(text=f"RAM: {ram}%")
        except Exception:
            pass
        self.after(5000, self._update_stats)

    def _on_closing(self):
        self.listener_active = False
        self.destroy()
        sys.exit(0)

    def _setup_callbacks(self):
        def _on_start():
            self.after(0, lambda: self.status_bar.set_status("speaking"))

        def _on_end():
            self.after(0, lambda: self.status_bar.set_status("active"))
            import voice.listener as listener_module
            listener_module.trigger_active_mode()

        speech_manager.on_speak_start = _on_start
        speech_manager.on_speak_end = _on_end


    def _process_and_respond(self, user_input: str, is_voice: bool = False):
        self.after(0, lambda: self.chat_panel.append_message(
            "You", user_input))

        def _worker():
            self.after(0, lambda: self.status_bar.set_status("thinking"))
            try:
                response = self.assistant.process_input(
                    user_input, is_voice=is_voice)
                
                if response and response != "IGNORE":
                    self.after(0, lambda r=response:
                               self.chat_panel.append_message("ROBIN", r))
            except Exception as e:
                logger.error(f"Process error: {e}")
                self.after(0, lambda: self.chat_panel.append_message(
                    "ROBIN", "Something went wrong. Please try again."))
            finally:
                self.after(0, lambda: self.status_bar.set_status("active"))

        threading.Thread(target=_worker, daemon=True).start()

    def start_background_listening(self):
        if self._listener_thread and self._listener_thread.is_alive():
            logger.info("[Listener] Restart prevented - thread already active")
            return

        self.listener_active = True
        self.last_listener_activity = time.time()

        if not self._watchdog_thread or not self._watchdog_thread.is_alive():
            self._watchdog_thread = threading.Thread(
                target=self._watchdog, daemon=True, name="Watchdog")
            self._watchdog_thread.start()

        self._listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="Listener")
        self._listener_thread.start()
        logger.info("[Listener] Started")

    def _watchdog(self):
        while self.listener_active:
            time.sleep(10)
            if self._listener_thread and not self._listener_thread.is_alive():
                logger.warning("Watchdog: Listener thread dead. Restarting...")
                self._listener_thread = threading.Thread(
                    target=self._listen_loop, daemon=True, name="Listener")
                self._listener_thread.start()
                logger.info("[Listener] Started")
            else:
                logger.debug("[Listener] Watchdog validated")

    def _listen_loop(self):
        logger.info("[Listener] Active")
        import voice.listener as listener_module
        pending_input = None

        while self.listener_active:
            try:
                self.last_listener_activity = time.time()

                # Buffer input spoken while ROBIN is speaking
                if speech_manager.is_speaking:
                    time.sleep(0.3)
                    continue

                # Process any buffered input immediately after speech ends
                if pending_input:
                    buffered = pending_input
                    pending_input = None
                    logger.info(
                        f"[Conversation] Buffered followup routed: "
                        f"{buffered!r}")
                    self._process_and_respond(buffered, is_voice=True)
                    continue

                # Update status
                is_listening = getattr(
                    listener_module, "_in_conversation", False)
                new_status = "listening" if is_listening else "active"
                if self.status_bar.get_status() != new_status:
                    self.after(0, lambda s=new_status:
                               self.status_bar.set_status(s))

                user_input = listen(timeout=3, phrase_time_limit=8)

                if not user_input:
                    continue

                # If ROBIN started speaking while we were listening
                # buffer it for after speech ends
                if speech_manager.is_speaking:
                    logger.info(
                        f"[Conversation] Buffering during speech: "
                        f"{user_input!r}")
                    pending_input = user_input
                    continue

                if user_input == "hey":
                    self.after(0, lambda: self.status_bar.set_status(
                        "listening"))
                    continue

                logger.info(f"Voice input: {user_input!r}")
                logger.info("[Conversation] Followup routed")
                self._process_and_respond(user_input, is_voice=True)

            except Exception as e:
                logger.error(f"Listener error: {e}")
                time.sleep(2)


def main():
    app = RobinApp()
    app.mainloop()


if __name__ == "__main__":
    main()