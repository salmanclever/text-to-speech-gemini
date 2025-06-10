import customtkinter as ctk
import os
from dotenv import load_dotenv
import gemini_tts
import text_utils
import pygame
import glob
import datetime
import time
import threading

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("مبدل متن به گفتار فارسی")
        self.geometry("900x800")
        ctk.set_appearance_mode("Light")

        self.default_font_family = "Vazirmatn"
        try:
            self.main_font = ctk.CTkFont(family=self.default_font_family, size=14)
            self.textbox_font = ctk.CTkFont(family=self.default_font_family, size=13)
            self.button_font = ctk.CTkFont(family=self.default_font_family, size=13, weight="bold")
            self.label_font = ctk.CTkFont(family=self.default_font_family, size=12)
            self.small_button_font = ctk.CTkFont(family=self.default_font_family, size=11)
        except Exception as e:
            print(f"Warning: Could not load Vazirmatn font. Using fallback. Error: {e}")
            self.main_font = ctk.CTkFont(size=14)
            self.textbox_font = ctk.CTkFont(size=13)
            self.button_font = ctk.CTkFont(size=13, weight="bold")
            self.label_font = ctk.CTkFont(size=12)
            self.small_button_font = ctk.CTkFont(size=11)

        # Define status_label_var early for use in mixer init error
        self.status_label_var = ctk.StringVar(value="وضعیت: آماده")

        try:
            pygame.mixer.init()
            print("Pygame mixer initialized.")
        except Exception as e:
            print(f"Error initializing pygame mixer: {e}")
            self.status_label_var.set("خطا در آماده‌سازی پخش کننده صدا!")

        self.current_audio_file = None
        self.audio_files_list = []
        self.audio_directory = "downloads/audio"
        os.makedirs(self.audio_directory, exist_ok=True)

        # UI Elements
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.main_frame.grid_columnconfigure(0, weight=1); self.main_frame.grid_columnconfigure(1, weight=3)
        self.main_frame.grid_rowconfigure(0, weight=0); self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=0); self.main_frame.grid_rowconfigure(3, weight=0)
        self.main_frame.grid_rowconfigure(4, weight=0); self.main_frame.grid_rowconfigure(5, weight=0)
        self.main_frame.grid_rowconfigure(6, weight=0)

        self.text_input_frame = ctk.CTkFrame(self.main_frame); self.text_input_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(10,0), pady=(0,5))
        self.text_input_frame.grid_columnconfigure(0, weight=1); self.text_input_frame.grid_rowconfigure(0, weight=0); self.text_input_frame.grid_rowconfigure(1, weight=1)
        self.text_input_label = ctk.CTkLabel(self.text_input_frame, text=":متن ورودی", font=self.main_font); self.text_input_label.grid(row=0, column=0, sticky="ne", padx=5, pady=(0,2))
        self.text_input = ctk.CTkTextbox(self.text_input_frame, font=self.textbox_font, wrap="word"); self.text_input.insert("0.0", "اینجا متن فارسی خود را وارد کنید..."); self.text_input.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0,5))

        self.controls_frame = ctk.CTkFrame(self.main_frame); self.controls_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0,5), pady=(0,5))
        self.speaker_label = ctk.CTkLabel(self.controls_frame, text=":انتخاب گوینده", font=self.main_font); self.speaker_label.pack(side="top", anchor="ne", padx=10, pady=(10,2))
        self.speaker_names = list(gemini_tts.AVAILABLE_SPEAKERS.keys()); self.speaker_variable = ctk.StringVar(value=self.speaker_names[0] if self.speaker_names else "N/A")
        self.speaker_menu = ctk.CTkOptionMenu(self.controls_frame, values=self.speaker_names, variable=self.speaker_variable, font=self.main_font, dropdown_font=self.main_font); self.speaker_menu.pack(side="top", fill="x", padx=10, pady=(0,20))

        self.convert_button = ctk.CTkButton(self.main_frame, text="تبدیل به گفتار", font=self.button_font, command=self.convert_action_threaded); self.convert_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(10,5))
        self.progress_bar = ctk.CTkProgressBar(self.main_frame); self.progress_bar.set(0); self.progress_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.status_label = ctk.CTkLabel(self.main_frame, textvariable=self.status_label_var, font=self.label_font, anchor="e"); self.status_label.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5, pady=(5,10))

        self.player_section_label = ctk.CTkLabel(self.main_frame, text="پخش کننده صدا", font=self.main_font); self.player_section_label.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(15,5))
        self.player_frame = ctk.CTkFrame(self.main_frame); self.player_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.player_frame.grid_columnconfigure(0, weight=1); self.player_frame.grid_columnconfigure(1, weight=0); self.player_frame.grid_columnconfigure(2, weight=0); self.player_frame.grid_columnconfigure(3, weight=0); self.player_frame.grid_columnconfigure(4, weight=2)
        self.audio_file_var = ctk.StringVar(value="فایلی انتخاب نشده")
        self.audio_select_menu = ctk.CTkOptionMenu(self.player_frame, variable=self.audio_file_var, values=[], font=self.label_font, dropdown_font=self.label_font, command=self.on_audio_file_select); self.audio_select_menu.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.play_button = ctk.CTkButton(self.player_frame, text="پخش", font=self.small_button_font, command=self.play_audio, width=70); self.play_button.grid(row=0, column=1, padx=5, pady=5)
        self.pause_button = ctk.CTkButton(self.player_frame, text="مکث", font=self.small_button_font, command=self.pause_audio, width=70); self.pause_button.grid(row=0, column=2, padx=5, pady=5)
        self.stop_button = ctk.CTkButton(self.player_frame, text="توقف", font=self.small_button_font, command=self.stop_audio, width=70); self.stop_button.grid(row=0, column=3, padx=5, pady=5)
        self.current_file_label_var = ctk.StringVar(value="فایل جاری: ندارد")
        self.current_file_label = ctk.CTkLabel(self.player_frame, textvariable=self.current_file_label_var, font=self.label_font, anchor="e"); self.current_file_label.grid(row=0, column=4, padx=10, pady=5, sticky="ew")

        # Initializations
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
            self.status_label_var.set("هشدار: کلید API برای Gemini تنظیم نشده است! لطفاً فایل .env را بررسی کنید.")
            self.convert_button.configure(state="disabled")
        else:
            # Test API configuration at startup gently
            # This print is for console debugging, status_label_var is for UI
            print(f"Attempting to configure Gemini with API key: ...{GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 4 else GEMINI_API_KEY}")
            config_error = gemini_tts.configure_gemini(GEMINI_API_KEY)
            if config_error:
                self.status_label_var.set(f"هشدار کلید API: {config_error}")
                self.convert_button.configure(state="disabled") # Disable if key is bad
            else:
                self.status_label_var.set("وضعیت: آماده (کلید API بارگذاری شد)")
                print("Gemini API key configured successfully via App.__init__.")


        self.refresh_audio_list()
        # Set initial state of player buttons
        self.on_audio_file_select(self.audio_file_var.get())


    def convert_action_threaded(self):
        # Disable button immediately, re-enable in logic
        self.convert_button.configure(state="disabled")

        # Clear previous error/status before starting new conversion
        # Check API key status before starting thread
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
             self.status_label_var.set("خطا: کلید API تنظیم نشده است. تبدیل لغو شد.")
             self.convert_button.configure(state="normal") # Re-enable button
             return

        # Initial check for API key validity before threading
        config_error = gemini_tts.configure_gemini(GEMINI_API_KEY)
        if config_error:
            self.status_label_var.set(f"خطا در کلید API: {config_error}. تبدیل لغو شد.")
            self.convert_button.configure(state="normal") # Re-enable button
            return

        self.status_label_var.set("در حال آماده سازی برای تبدیل...")
        self.progress_bar.set(0) # Reset progress bar
        self.update_idletasks()

        thread = threading.Thread(target=self.convert_action_logic)
        thread.daemon = True
        thread.start()

    def convert_action_logic(self):
        api_key = GEMINI_API_KEY

        text_to_convert = self.text_input.get("0.0", "end-1c").strip()
        if not text_to_convert:
            self.status_label_var.set("خطا: متن ورودی خالی است. لطفاً متنی را وارد کنید.")
            self.convert_button.configure(state="normal")
            self.progress_bar.set(0)
            return

        selected_speaker_name = self.speaker_variable.get()
        speaker_id = gemini_tts.AVAILABLE_SPEAKERS.get(selected_speaker_name)
        if not speaker_id: # Should not happen if dropdown is populated correctly
            self.status_label_var.set(f"خطا: شناسه گوینده برای '{selected_speaker_name}' یافت نشد.")
            self.convert_button.configure(state="normal")
            self.progress_bar.set(0)
            return

        self.status_label_var.set("در حال تقسیم‌بندی متن...")
        self.update_idletasks()

        chunks = text_utils.split_text_into_chunks(text_to_convert, max_length=text_utils.MAX_CHUNK_LENGTH)

        if not chunks:
            self.status_label_var.set("خطا: متنی برای تبدیل وجود ندارد (پس از تقسیم‌بندی).")
            self.convert_button.configure(state="normal")
            self.progress_bar.set(0)
            return

        total_chunks = len(chunks)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        successful_conversions = 0
        # encountered_error = False # Not currently used, but could be if we want to stop on first error

        for i, chunk in enumerate(chunks):
            self.status_label_var.set(f"در حال تبدیل قطعه {i+1} از {total_chunks}...")
            current_progress = (i) / total_chunks
            self.progress_bar.set(current_progress)
            self.update_idletasks()

            output_filename = f"output_{timestamp}_part_{i+1}.mp3"
            output_filepath = os.path.join(self.audio_directory, output_filename)

            # No try-except here for the TTS call itself, gemini_tts.text_to_audio handles its own errors
            # and returns them as part of its tuple.
            audio_file_path, error_message = gemini_tts.text_to_audio(
                api_key=api_key,
                text_prompt=chunk,
                speaker_id=speaker_id,
                output_filepath=output_filepath
            )

            if error_message:
                self.status_label_var.set(f"خطا در قطعه {i+1}: {error_message[:100]}") # Show first 100 chars of error
                print(f"Error converting chunk {i+1}: {error_message}")
                # Optionally break, or continue with next chunks. Current: continue.
                # time.sleep(1) # Brief pause to let user read error, not good for real app
            elif audio_file_path and os.path.exists(audio_file_path):
                print(f"Chunk {i+1} successfully converted to {audio_file_path}")
                successful_conversions += 1
            else: # Should ideally not happen if error_message is None and no path
                self.status_label_var.set(f"خطای ناشناخته در تبدیل قطعه {i+1}.")
                print(f"Unknown error for chunk {i+1}. No path and no error message from gemini_tts.")

            self.progress_bar.set((i + 1) / total_chunks) # Update progress after processing the chunk
            self.update_idletasks()

            if error_message and not GEMINI_API_KEY.startswith("YOUR_API_KEY_HERE"): # If real API key and error, stop
                 print("Stopping due to error with a real API key.")
                 break


        if successful_conversions == total_chunks and total_chunks > 0:
            self.status_label_var.set(f"تبدیل کامل شد! {successful_conversions} فایل صوتی با موفقیت ذخیره شد.")
        elif successful_conversions > 0:
             self.status_label_var.set(f"پردازش کامل شد. {successful_conversions} از {total_chunks} فایل ذخیره شد (برخی با خطا).")
        elif total_chunks > 0:
            self.status_label_var.set("پردازش کامل شد، اما هیچ فایل صوتی با موفقیت ذخیره نشد. کنسول را بررسی کنید.")
        else: # Should be caught by earlier checks if chunks list was empty
            self.status_label_var.set("هیچ قطعه‌ای برای پردازش ارسال نشد.")


        self.refresh_audio_list()
        self.convert_button.configure(state="normal")
        # Set progress to full only if all chunks were processed, otherwise reflect partial success/failure
        if total_chunks > 0 :
            self.progress_bar.set(float(successful_conversions)/total_chunks)
        else:
            self.progress_bar.set(0)

        self.update_idletasks()

    def refresh_audio_list(self):
        try:
            if not os.path.exists(self.audio_directory):
                os.makedirs(self.audio_directory)

            self.audio_files_list = sorted(
                [os.path.basename(f) for f in glob.glob(os.path.join(self.audio_directory, "*.mp3")) + \
                                             glob.glob(os.path.join(self.audio_directory, "*.wav"))],
                key=lambda f: os.path.getmtime(os.path.join(self.audio_directory, f)),
                reverse=True
            )
            display_values = self.audio_files_list
            current_selection = self.audio_file_var.get() # Preserve current selection if still valid

            if not display_values:
                display_values = ["فایلی یافت نشد"]
                self.audio_select_menu.configure(values=display_values, state="disabled")
                self.audio_file_var.set(display_values[0])
            else:
                self.audio_select_menu.configure(values=display_values, state="normal")
                if current_selection not in display_values or current_selection in ["فایلی یافت نشد", "خطا"]:
                     self.audio_file_var.set(display_values[0]) # Default to newest if old selection gone
                else:
                    self.audio_file_var.set(current_selection) # Restore valid selection

            self.on_audio_file_select(self.audio_file_var.get())

        except Exception as e:
            print(f"Error refreshing audio list: {e}")
            self.status_label_var.set("خطا در خواندن لیست فایل‌های صوتی.")
            if hasattr(self, 'audio_select_menu'):
                self.audio_select_menu.configure(values=["خطا"], state="disabled")
                self.audio_file_var.set("خطا")

    def on_audio_file_select(self, selected_file_basename):
        is_valid_file = selected_file_basename and selected_file_basename not in ["فایلی یافت نشد", "خطا"]
        if is_valid_file:
            self.current_audio_file = os.path.join(self.audio_directory, selected_file_basename)
            self.current_file_label_var.set(f"فایل جاری: {selected_file_basename}")
        else:
            self.current_audio_file = None
            self.current_file_label_var.set("فایل جاری: ندارد")

        # Enable/disable player buttons
        button_state = "normal" if is_valid_file else "disabled"
        if hasattr(self, 'play_button'): self.play_button.configure(state=button_state)
        if hasattr(self, 'pause_button'): self.pause_button.configure(state=button_state)
        if hasattr(self, 'stop_button'): self.stop_button.configure(state=button_state)


    def play_audio(self):
        if self.current_audio_file and os.path.exists(self.current_audio_file):
            try:
                current_time = pygame.mixer.music.get_pos() / 1000.0 # seconds
                is_paused = not pygame.mixer.music.get_busy() and current_time > 0 # Heuristic for paused

                if pygame.mixer.music.get_busy() and not is_paused: # Currently playing
                     # Optional: restart playback or do nothing
                     # For now, let it continue playing. Or, restart:
                     # pygame.mixer.music.stop()
                     # pygame.mixer.music.load(self.current_audio_file)
                     # pygame.mixer.music.play()
                     # self.status_label_var.set(f"بازپخش: {os.path.basename(self.current_audio_file)}")
                     print("Already playing. To restart, stop first or handle here.")
                     return # Or allow to "restart" by falling through
                elif is_paused: # Was paused
                     pygame.mixer.music.unpause()
                     self.status_label_var.set(f"ادامه پخش: {os.path.basename(self.current_audio_file)}")
                else: # Not playing, not paused (i.e. fresh play or stopped)
                    pygame.mixer.music.load(self.current_audio_file)
                    pygame.mixer.music.play()
                    self.status_label_var.set(f"در حال پخش: {os.path.basename(self.current_audio_file)}")
            except Exception as e:
                print(f"Error playing audio: {e}")
                self.status_label_var.set(f"خطا در پخش صدا: {str(e)[:100]}")
        else:
            self.status_label_var.set("فایل صوتی برای پخش انتخاب نشده یا یافت نشد.")

    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.status_label_var.set("پخش متوقف شد (مکث).")

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.status_label_var.set("پخش متوقف شد.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
