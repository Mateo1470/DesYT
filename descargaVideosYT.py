import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import yt_dlp
import os
import threading
import re

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡ Descarga videos YT")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e2f")
        # Debe ser la carpeta que contiene ffmpeg.exe, no el ejecutable completo
        self.ffmpeg_ruta = r'C:\ffmpeg\bin'  

        self.fuente = ("Segoe UI", 11)
        self.entry_style = {"font": self.fuente, "bg": "#2e2e3f", "fg": "#00ffcc", "insertbackground": "#00ffcc", "relief": "flat"}
        self.label_style = {"font": ("Segoe UI", 12, "bold"), "bg": "#1e1e2f", "fg": "#00ffcc"}
        self.button_style = {"font": self.fuente, "bg": "#00ffcc", "fg": "#1e1e2f", "relief": "flat", "activebackground": "#00d1a0"}

        self.crear_widgets()

    def crear_widgets(self):
        tk.Label(self.root, text="🎥 URL del video/audio:", **self.label_style).pack(pady=10)
        self.entry_url = tk.Entry(self.root, width=50, **self.entry_style)
        self.entry_url.pack(pady=5)
        self.entry_url.bind("<Return>", lambda event: self.iniciar_descarga())

        tk.Label(self.root, text="📁 Ruta de destino:", **self.label_style).pack(pady=10)
        self.entry_ruta = tk.Entry(self.root, width=50, **self.entry_style)
        self.entry_ruta.pack(pady=5)

        tk.Button(self.root, text="Seleccionar carpeta", command=self.seleccionar_ruta_destino, **self.button_style).pack(pady=5)

        tk.Label(self.root, text="🔽 Formato de descarga:", **self.label_style).pack(pady=10)
        self.combo_resolucion = tk.StringVar(value="bestvideo+bestaudio/best")
        combo = tk.OptionMenu(self.root, self.combo_resolucion, 
                              "bestvideo+bestaudio/best", 
                              "bestaudio", 
                              "bestvideo",
                              "mp4")  # Nueva opción agregada
        combo.config(**self.button_style, width=30)
        combo["menu"].config(bg="#2e2e3f", fg="#00ffcc", font=self.fuente)
        combo.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=300)
        self.progress.pack(pady=10)

        tk.Button(self.root, text="🚀 Iniciar Descarga", command=self.iniciar_descarga, **self.button_style).pack(pady=25)

    def seleccionar_ruta_destino(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, ruta)

    def limpiar_titulo(self, title):
        # Remueve caracteres inválidos en nombres de archivo Windows
        return re.sub(r'[\\/*?:"<>|]', "", title)

    def iniciar_descarga(self):
        url = self.entry_url.get().strip()
        ruta_destino = self.entry_ruta.get().strip()
        resolucion = self.combo_resolucion.get()

        if not url or not ruta_destino:
            messagebox.showwarning("Advertencia", "Completa todos los campos.")
            return

        if not url.startswith("http"):
            messagebox.showerror("Error", "URL inválida.")
            return

        if not os.path.exists(self.ffmpeg_ruta):
            messagebox.showerror("FFmpeg no encontrado", f"No se encontró ffmpeg en:\n{self.ffmpeg_ruta}")
            return

        if not os.path.exists(ruta_destino):
            os.makedirs(ruta_destino)

        hilo = threading.Thread(target=self.descargar_video, args=(url, ruta_destino, resolucion))
        hilo.start()

    def descargar_video(self, url, ruta_destino, resolucion):
        self.progress.start()
        try:
            opciones = {
                'format': 'bestvideo+bestaudio/best' if resolucion == 'mp4' else resolucion,
                'outtmpl': os.path.join(ruta_destino, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'ffmpeg_location': self.ffmpeg_ruta,
                'quiet': True,
            }

            # Evitar caracteres inválidos en títulos
            def sanitize_filename(d):
                if 'title' in d:
                    d['title'] = self.limpiar_titulo(d['title'])
                return d
            opciones['progress_hooks'] = [lambda d: sanitize_filename(d)]

            # Postprocesadores según formato
            if resolucion == "bestaudio":
                opciones['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif resolucion == "mp4":
                opciones['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }]

            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])

            messagebox.showinfo("Éxito", f"Descarga completada en:\n{ruta_destino}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error:\n{e}")
        finally:
            self.progress.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
