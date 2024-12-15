import os
import shutil
import time
import tkinter as tk
from tkinter import ttk
import threading

# Fonction pour copier les fichiers du lecteur source vers le lecteur cible
def sync_usb_drives(source, target, stats):
    for root, dirs, files in os.walk(source):
        relative_path = os.path.relpath(root, source)
        target_path = os.path.join(target, relative_path)
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            stats['folders_created'] += 1
        
        for file in files:
            source_file = os.path.join(root, file)
            target_file = os.path.join(target_path, file)
            
            if not os.path.exists(target_file) or os.path.getmtime(source_file) > os.path.getmtime(target_file):
                shutil.copy2(source_file, target_file)
                stats['files_copied'] += 1

# Interface graphique
class USBBackupApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Synchronisation de Clés USB")
        self.geometry("600x500")
        self.configure(bg="#1E1E2F")
        
        # Variables pour les statistiques
        self.stats = {'files_copied': 0, 'folders_created': 0, 'sync_duration': 0}
        
        # Chemins des lecteurs source et cible
        self.source_path = "H:\\"
        self.target_path = "F:\\"
        
        # Widgets de l'interface
        self.create_widgets()
        
        # Lancement du thread de détection automatique des clés USB
        self.monitor_usb_thread = threading.Thread(target=self.monitor_usb_drives, daemon=True)
        self.monitor_usb_thread.start()
    
    def create_widgets(self):
        # Titre principal
        title_label = tk.Label(self, text="Synchronisation de Clés USB", font=("Helvetica", 20, "bold"), bg="#1E1E2F", fg="#F0F0F0")
        title_label.pack(pady=20)
        
        # Bouton de lancement de la synchronisation
        self.sync_button = tk.Button(self, text="Lancer la Synchronisation", font=("Helvetica", 14), command=self.start_sync, bg="#4CAF50", fg="white", relief="flat", cursor="hand2")
        self.sync_button.pack(pady=20)
        
        # Conteneur des statistiques
        self.stats_frame = tk.Frame(self, bg="#1E1E2F")
        self.stats_frame.pack(pady=20)
        
        self.stats_labels = {
            'files_copied': tk.Label(self.stats_frame, text="Fichiers copiés : 0", font=("Helvetica", 12), bg="#1E1E2F", fg="#F0F0F0"),
            'folders_created': tk.Label(self.stats_frame, text="Dossiers créés : 0", font=("Helvetica", 12), bg="#1E1E2F", fg="#F0F0F0"),
            'sync_duration': tk.Label(self.stats_frame, text="Durée de synchronisation : 0s", font=("Helvetica", 12), bg="#1E1E2F", fg="#F0F0F0")
        }
        
        for label in self.stats_labels.values():
            label.pack(pady=5)
        
        # Barre d'état
        self.status_label = tk.Label(self, text="En attente...", font=("Helvetica", 12), relief="sunken", anchor="w", bg="#2C2F33", fg="#F0F0F0")
        self.status_label.pack(fill="x", pady=10)
    
    def start_sync(self):
        source = self.source_path
        target = self.target_path
        
        if not os.path.exists(source):
            self.status_label.config(text="Le lecteur source est introuvable.")
            return
        if not os.path.exists(target):
            self.status_label.config(text="Le lecteur cible est introuvable.")
            return
        
        self.sync_button.config(state="disabled")
        self.status_label.config(text="Synchronisation en cours...")
        self.stats = {'files_copied': 0, 'folders_created': 0, 'sync_duration': 0}  # Réinitialise les statistiques
        start_time = time.time()
        
        try:
            sync_usb_drives(source, target, self.stats)
            self.stats['sync_duration'] = round(time.time() - start_time, 2)
            self.update_stats()
            self.status_label.config(text="Synchronisation terminée avec succès.")
        except Exception as e:
            self.status_label.config(text=f"Erreur : {e}")
        finally:
            self.sync_button.config(state="normal")
    
    def update_stats(self):
        self.stats_labels['files_copied'].config(text=f"Fichiers copiés : {self.stats['files_copied']}")
        self.stats_labels['folders_created'].config(text=f"Dossiers créés : {self.stats['folders_created']}")
        self.stats_labels['sync_duration'].config(text=f"Durée de synchronisation : {self.stats['sync_duration']}s")
    
    def monitor_usb_drives(self):
        while True:
            source_exists = os.path.exists(self.source_path)
            target_exists = os.path.exists(self.target_path)
            
            if source_exists and target_exists:
                self.status_label.config(text="Détection des deux clés. Synchronisation automatique...")
                self.start_sync()
            time.sleep(5)  # Vérifie la connexion toutes les 5 secondes

if __name__ == "__main__":
    app = USBBackupApp()
    app.mainloop()
