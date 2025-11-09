import os
import sys
import time
import gc
import threading
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count, Manager
import pymupdf
import customtkinter as ctk
from tkinter import filedialog
from datetime import datetime
from queue import Queue, Empty

# Configuration CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ═══════════════════════════════════════════════════════════════════
# 🔥💀 CONFIGURATION ULTRA-HARDCORE - MODE DEMON 💀🔥
# ═══════════════════════════════════════════════════════════════════

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
sys.setrecursionlimit(10000)


class PDFSearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuration fenêtre principale
        self.title("🔥💀 PDF TURBO SCAN - DEMON MODE 💀🔥")
        self.geometry("1000x700")
        
        # Variables
        self.directory_path = ctk.StringVar(value="Sélectionnez un dossier...")
        self.output_path = ctk.StringVar(value="Choisir l'emplacement des résultats...")
        self.search_terms = []
        self.is_running = False
        self.found_count = 0
        self.processed_count = 0
        self.total_files = 0
        self.start_time = 0
        
        # Queue pour communication asynchrone (pas de ralentissement)
        self.update_queue = Queue()
        
        self.setup_ui()
        self.start_queue_processor()
        
    def setup_ui(self):
        # ═══════════════════════════════════════════════════════════
        # HEADER SECTION
        # ═══════════════════════════════════════════════════════════
        header_frame = ctk.CTkFrame(self, fg_color=("#1a1a2e", "#0f0f1e"), corner_radius=15)
        header_frame.pack(pady=20, padx=20, fill="x")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔥💀 PDF TURBO SCAN - DEMON MODE 💀🔥",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("#ff4444", "#ff6666")
        )
        title_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Mode Demon - Vitesse Maximale - Zero Compromis",
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color=("#888888", "#aaaaaa")
        )
        subtitle_label.pack(pady=(0, 15))
        
        # ═══════════════════════════════════════════════════════════
        # CONFIGURATION SECTION
        # ═══════════════════════════════════════════════════════════
        config_frame = ctk.CTkFrame(self, corner_radius=15)
        config_frame.pack(pady=10, padx=20, fill="x")
        
        # Dossier d'entrée
        folder_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        folder_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            folder_frame,
            text="📁 Dossier PDF:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.folder_entry = ctk.CTkEntry(
            folder_frame,
            textvariable=self.directory_path,
            width=500,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.folder_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            folder_frame,
            text="📂 Parcourir",
            command=self.select_directory,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1976D2", "#1565C0")
        ).pack(side="left", padx=5)
        
        # Fichier de sortie
        output_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        output_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            output_frame,
            text="💾 Résultats:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))
        
        self.output_entry = ctk.CTkEntry(
            output_frame,
            textvariable=self.output_path,
            width=500,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.output_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            output_frame,
            text="💾 Choisir",
            command=self.select_output,
            width=120,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1976D2", "#1565C0")
        ).pack(side="left", padx=5)
        
        # Termes de recherche
        search_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        search_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            search_frame,
            text="🔍 Termes de recherche (un par ligne):",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w")
        
        self.search_textbox = ctk.CTkTextbox(
            search_frame,
            width=700,
            height=100,
            font=ctk.CTkFont(size=12),
            corner_radius=10
        )
        self.search_textbox.pack(pady=5, fill="x")
        self.search_textbox.insert("1.0", "cablage\nelectrique")
        
        # ═══════════════════════════════════════════════════════════
        # STATS SECTION
        # ═══════════════════════════════════════════════════════════
        stats_frame = ctk.CTkFrame(self, corner_radius=15)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(pady=15, padx=20)
        
        # Stat boxes
        self.stat_total = self.create_stat_box(stats_grid, "📊 Total", "0", 0, 0)
        self.stat_processed = self.create_stat_box(stats_grid, "⚡ Traités", "0", 0, 1)
        self.stat_found = self.create_stat_box(stats_grid, "🎯 Trouvés", "0", 0, 2)
        self.stat_speed = self.create_stat_box(stats_grid, "🚀 Vitesse", "0/s", 0, 3)
        
        # Barre de progression
        progress_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        progress_frame.pack(pady=10, padx=20, fill="x")
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=900,
            height=25,
            corner_radius=10
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0% | ETA: --",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.progress_label.pack()
        
        # ═══════════════════════════════════════════════════════════
        # CONTROL BUTTONS
        # ═══════════════════════════════════════════════════════════
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=15)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="🚀 LANCER LA RECHERCHE DEMON",
            command=self.start_search,
            width=250,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#ff4444", "#cc0000"),
            hover_color=("#cc0000", "#990000"),
            corner_radius=15
        )
        self.start_button.pack(side="left", padx=10)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="⛔ ARRÊTER",
            command=self.stop_search,
            width=150,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#ff9800", "#f57c00"),
            hover_color=("#f57c00", "#e65100"),
            corner_radius=15,
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="🎨 Thème",
            command=self.toggle_theme,
            width=100,
            height=50,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#9c27b0", "#7b1fa2"),
            hover_color=("#7b1fa2", "#6a1b9a"),
            corner_radius=15
        ).pack(side="left", padx=10)
        
        # ═══════════════════════════════════════════════════════════
        # LOG SECTION
        # ═══════════════════════════════════════════════════════════
        log_frame = ctk.CTkFrame(self, corner_radius=15)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            log_frame,
            text="📝 Console de sortie",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Courier", size=11),
            corner_radius=10
        )
        self.log_textbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.log("✅ Application initialisée - Prêt pour le mode DEMON!")
        self.log("⚡ Configuration: Vitesse MAXIMALE - Zero overhead")
        
    def create_stat_box(self, parent, title, value, row, col):
        frame = ctk.CTkFrame(parent, width=200, height=80, corner_radius=10)
        frame.grid(row=row, column=col, padx=10, pady=5)
        frame.grid_propagate(False)
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=12)
        ).pack(pady=(10, 0))
        
        value_label = ctk.CTkLabel(
            frame,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#00ff00", "#00cc00")
        )
        value_label.pack(pady=(5, 10))
        
        return value_label
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.log_textbox.see("end")
    
    def start_queue_processor(self):
        """Process updates from queue - runs every 100ms (non-blocking)"""
        try:
            while True:
                update_type, data = self.update_queue.get_nowait()
                
                if update_type == "stats":
                    self.stat_processed.configure(text=f"{data['processed']:,}")
                    self.stat_found.configure(text=f"{data['found']:,}")
                    self.stat_speed.configure(text=f"{data['speed']:.1f}/s")
                    
                    progress = data['progress']
                    self.progress_bar.set(progress)
                    
                    eta = data.get('eta', '--')
                    self.progress_label.configure(text=f"{progress*100:.1f}% | ETA: {eta}")
                    
                elif update_type == "log":
                    self.log(data)
                    
        except Empty:
            pass
        
        # Re-schedule (100ms interval = 10 updates/sec max, minimal overhead)
        self.after(100, self.start_queue_processor)
        
    def select_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.directory_path.set(folder)
            self.log(f"📁 Dossier sélectionné: {folder}")
            
    def select_output(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )
        if file:
            self.output_path.set(file)
            self.log(f"💾 Fichier de sortie: {file}")
    
    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        self.log(f"🎨 Thème changé: {new_mode}")
    
    def start_search(self):
        # Validation
        if self.directory_path.get() == "Sélectionnez un dossier...":
            self.log("❌ Erreur: Veuillez sélectionner un dossier!")
            return
            
        if self.output_path.get() == "Choisir l'emplacement des résultats...":
            self.log("❌ Erreur: Veuillez choisir un fichier de sortie!")
            return
        
        # Récupérer les termes de recherche
        search_text = self.search_textbox.get("1.0", "end-1c")
        self.search_terms = list(set([
            term.strip().lower() 
            for term in search_text.split("\n") 
            if term.strip()
        ]))
        
        if not self.search_terms:
            self.log("❌ Erreur: Veuillez entrer au moins un terme de recherche!")
            return
        
        self.log(f"🔍 Termes: {', '.join(self.search_terms)}")
        
        # Reset stats
        self.found_count = 0
        self.processed_count = 0
        self.progress_bar.set(0)
        
        # Démarrer la recherche dans un thread séparé
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        
        search_thread = threading.Thread(target=self.run_search, daemon=True)
        search_thread.start()
    
    def stop_search(self):
        self.is_running = False
        self.update_queue.put(("log", "⚠️ Arrêt demandé..."))
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
    
    def run_search(self):
        self.start_time = time.time()
        
        self.update_queue.put(("log", "╔" + "═" * 60 + "╗"))
        self.update_queue.put(("log", "║  🔥💀 DEMON MODE ACTIVÉ 💀🔥".center(62) + "║"))
        self.update_queue.put(("log", "╚" + "═" * 60 + "╝"))
        
        # Phase 1: Scan des fichiers
        self.update_queue.put(("log", "\n📂 [PHASE 1] Scan du système de fichiers..."))
        scan_start = time.time()
        
        pdf_files = [
            os.path.join(root, file)
            for root, dirs, files in os.walk(self.directory_path.get())
            for file in files
            if file.lower().endswith('.pdf')
        ]
        
        scan_time = time.time() - scan_start
        self.total_files = len(pdf_files)
        self.stat_total.configure(text=f"{self.total_files:,}")
        self.update_queue.put(("log", f"✅ {self.total_files:,} fichiers PDF détectés en {scan_time:.2f}s"))
        
        if self.total_files == 0:
            self.update_queue.put(("log", "❌ Aucun fichier PDF trouvé!"))
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            return
        
        # Phase 2: Configuration DEMON MODE
        num_cpus = cpu_count()
        optimal_workers = min(num_cpus * 6, 61)
        
        self.update_queue.put(("log", f"\n🚀 [PHASE 2] Configuration DEMON:"))
        self.update_queue.put(("log", f"   💻 CPU Cores: {num_cpus}"))
        self.update_queue.put(("log", f"   ⚡ Workers: {optimal_workers} (surallocation: {optimal_workers/num_cpus:.1f}x)"))
        self.update_queue.put(("log", f"   💾 RAM: Optimisée (GC désactivé)"))
        self.update_queue.put(("log", f"   🎯 Mode: VITESSE MAXIMALE"))
        
        # Phase 3: Traitement ULTRA-RAPIDE
        self.update_queue.put(("log", f"\n⚡ [PHASE 3] Traitement DEMON en cours...\n"))
        
        found_files = []
        error_files = []
        self.processed_count = 0
        self.found_count = 0
        
        # Désactiver GC pour vitesse maximale
        gc.disable()
        
        try:
            with ProcessPoolExecutor(
                max_workers=optimal_workers,
                initializer=init_worker
            ) as executor:
                # Soumettre tous les jobs immédiatement
                futures = {
                    executor.submit(
                        search_in_pdf_demon_mode,
                        pdf,
                        self.search_terms
                    ): pdf
                    for pdf in pdf_files
                }
                
                last_update_time = time.time()
                update_interval = 0.5  # Mettre à jour GUI seulement toutes les 0.5s (pas de ralentissement)
                
                for future in as_completed(futures):
                    if not self.is_running:
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    
                    self.processed_count += 1
                    
                    try:
                        pdf_path, page_num, found, error = future.result(timeout=60)
                        
                        if error:
                            error_files.append({'file': pdf_path, 'error': error})
                        elif found:
                            found_files.append({'file': pdf_path, 'page': page_num})
                            self.found_count += 1
                        
                        # Update GUI seulement toutes les 0.5s (OPTIMISATION CRITIQUE)
                        current_time = time.time()
                        if current_time - last_update_time >= update_interval:
                            elapsed = current_time - self.start_time
                            speed = self.processed_count / elapsed if elapsed > 0 else 0
                            progress = self.processed_count / self.total_files
                            
                            remaining = self.total_files - self.processed_count
                            eta_seconds = remaining / speed if speed > 0 else 0
                            eta_min = int(eta_seconds // 60)
                            eta_sec = int(eta_seconds % 60)
                            eta = f"{eta_min}m{eta_sec}s"
                            
                            self.update_queue.put(("stats", {
                                'processed': self.processed_count,
                                'found': self.found_count,
                                'speed': speed,
                                'progress': progress,
                                'eta': eta
                            }))
                            
                            last_update_time = current_time
                        
                    except Exception as e:
                        error_files.append({'file': futures[future], 'error': str(e)})
        
        finally:
            gc.enable()
        
        # Dernière mise à jour finale
        elapsed = time.time() - self.start_time
        speed = self.processed_count / elapsed if elapsed > 0 else 0
        self.update_queue.put(("stats", {
            'processed': self.processed_count,
            'found': self.found_count,
            'speed': speed,
            'progress': 1.0,
            'eta': '0m0s'
        }))
        
        # Phase 4: Résultats
        if self.is_running:
            self.save_results(found_files, error_files, elapsed)
            self.update_queue.put(("log", "\n🏆 TRAITEMENT TERMINÉ!"))
            self.update_queue.put(("log", f"⏱️  Temps total: {elapsed:.2f}s ({elapsed/60:.2f} min)"))
            self.update_queue.put(("log", f"⚡ Vitesse moyenne: {speed:.2f} fichiers/seconde"))
            self.update_queue.put(("log", f"🚀 Throughput: {self.total_files / (elapsed/60):.0f} fichiers/minute"))
            self.update_queue.put(("log", f"🎯 Trouvés: {len(found_files):,} | Erreurs: {len(error_files):,}"))
            self.update_queue.put(("log", f"💀 L'ordinateur a survécu... cette fois 💀"))
        else:
            self.update_queue.put(("log", "\n⚠️ TRAITEMENT INTERROMPU!"))
        
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.is_running = False
    
    def save_results(self, found_files, error_files, elapsed):
        with open(self.output_path.get(), 'w', encoding='utf-8') as f:
            f.write("╔" + "═" * 78 + "╗\n")
            f.write("║  🔥💀 RÉSULTATS DEMON MODE - Recherche multiple 💀🔥  " + " " * 19 + "║\n")
            f.write("╚" + "═" * 78 + "╝\n\n")
            
            f.write(f"📁 Dossier: {self.directory_path.get()}\n")
            f.write(f"📊 Fichiers analysés: {self.total_files:,}\n")
            f.write(f"✅ Fichiers trouvés: {len(found_files):,}\n")
            f.write(f"❌ Erreurs: {len(error_files):,}\n")
            f.write(f"⚡ Vitesse: {self.total_files/elapsed:.2f} PDF/s\n")
            f.write(f"⏱️  Temps: {elapsed:.2f}s ({elapsed/60:.2f} min)\n")
            f.write("─" * 80 + "\n\n")
            
            if found_files:
                f.write("🎯 FICHIERS CONTENANT TERMES RECHERCHÉS:\n")
                f.write("=" * 80 + "\n\n")
                for idx, result in enumerate(found_files, 1):
                    f.write(f"{idx:5d}. 📄 {result['file']}\n")
                    f.write(f"       └─ 📖 Page {result['page']}\n\n")
            else:
                f.write("❌ Aucun fichier contenant les termes recherchés trouvé.\n\n")
            
            if error_files:
                f.write("\n⚠️ ERREURS:\n")
                f.write("=" * 80 + "\n\n")
                for idx, result in enumerate(error_files, 1):
                    f.write(f"{idx:4d}. ❌ {result['file']}\n")
                    f.write(f"       └─ {result['error']}\n\n")
        
        self.update_queue.put(("log", f"\n💾 Résultats sauvegardés: {self.output_path.get()}"))


def init_worker():
    """DEMON MODE worker - désactiver GC et booster priorité"""
    gc.disable()
    try:
        import psutil
        p = psutil.Process()
        if sys.platform == 'win32':
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
            p.nice(-10)
    except:
        pass


def search_in_pdf_demon_mode(pdf_path, search_terms):
    """🔥💀 DEMON MODE - Multi-term search avec early exit 💀🔥"""
    doc = None
    try:
        doc = pymupdf.open(pdf_path)
        for page_num in range(doc.page_count):
            text = doc[page_num].get_text("text").lower()
            if any(term in text for term in search_terms):
                doc.close()
                return (pdf_path, page_num + 1, True, None)
        doc.close()
        return (pdf_path, -1, False, None)
    except Exception as e:
        if doc:
            try:
                doc.close()
            except:
                pass
        return (pdf_path, -1, False, str(e))


if __name__ == "__main__":
    app = PDFSearchApp()
    app.mainloop()
