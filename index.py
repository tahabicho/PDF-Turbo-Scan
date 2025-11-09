import os
import sys
import time
import gc
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
import pymupdf

# ═══════════════════════════════════════════════════════════════════
# 🔥💀 CONFIGURATION ULTRA-HARDCORE - MODE DEMON 💀🔥
# ═══════════════════════════════════════════════════════════════════

# Désactiver TOUTES les limitations de threads
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"

# Optimisations Python niveau système
sys.setrecursionlimit(10000)

# Précompilation - recherche ultra-rapide
SEARCH_TERM = "banque"


def search_in_pdf_demon_mode(pdf_path):
    """
    🔥💀 VERSION DEMON MODE - Optimisée à mort 💀🔥
    """
    doc = None
    try:
        doc = pymupdf.open(pdf_path)
        
        # Early exit ultra-optimisé
        for page_num in range(doc.page_count):
            # Extraction texte mode "text" (le plus rapide)
            text = doc[page_num].get_text("text").lower()
            
            # Recherche inline ultra-rapide
            if SEARCH_TERM in text:
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


def init_worker():
    """
    Initialisation DEMON MODE de chaque worker
    """
    # Désactiver GC (gain 10-20%)
    gc.disable()
    
    # Augmenter la priorité processus
    try:
        import psutil
        p = psutil.Process()
        if sys.platform == 'win32':
            p.nice(psutil.HIGH_PRIORITY_CLASS)
        else:
            p.nice(-10)
    except:
        pass


def progress_bar_demon(current, total, start_time, found_count, bar_length=50):
    """
    Barre de progression DEMON avec stats temps réel
    """
    percent = float(current) / total
    filled = int(round(percent * bar_length))
    bar = '█' * filled + '░' * (bar_length - filled)
    
    elapsed = time.time() - start_time
    speed = current / elapsed if elapsed > 0 else 0
    eta_seconds = (total - current) / speed if speed > 0 else 0
    
    eta_min = int(eta_seconds // 60)
    eta_sec = int(eta_seconds % 60)
    
    # Calculer le % de complétion estimé
    remaining = total - current
    
    print(f'\r🔥💀 [{bar}] {current:,}/{total:,} ({percent*100:.1f}%) | '
          f'⚡ {speed:.1f} PDF/s | 🎯 {found_count} trouvés | '
          f'📉 Reste: {remaining:,} | ⏱️  ETA: {eta_min}m{eta_sec}s', 
          end='', flush=True)


def main(directory_path, output_file="resultats_ventec.txt"):
    """
    🔥💀 FONCTION PRINCIPALE DEMON MODE 💀🔥
    """
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + "🔥💀 MODE DEMON ACTIVÉ - L'ENFER COMMENCE 💀🔥".center(80) + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    start_time = time.time()
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 1: Scan ultra-rapide
    # ═══════════════════════════════════════════════════════════════
    print("📂 [PHASE 1] Scan du système de fichiers...")
    scan_start = time.time()
    
    pdf_files = [
        os.path.join(root, file)
        for root, dirs, files in os.walk(directory_path)
        for file in files
        if file.lower().endswith('.pdf')
    ]
    
    scan_time = time.time() - scan_start
    total_files = len(pdf_files)
    
    print(f"   ✅ {total_files:,} fichiers PDF détectés en {scan_time:.2f}s\n")
    
    if total_files == 0:
        print("❌ Aucun fichier PDF trouvé!")
        return
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 2: Configuration DEMON MODE
    # ═══════════════════════════════════════════════════════════════
    num_cpus = cpu_count()
    
    # OPTIMAL pour I/O-bound: 4-6x CPU (équilibre CPU/disque)
    optimal_workers = min(num_cpus * 6, 61)  # Max 61 sur Windows
    
    print("🚀 [PHASE 2] Configuration DEMON MODE:")
    print(f"   💻 CPU Cores: {num_cpus}")
    print(f"   ⚡ Workers: {optimal_workers} (surallocation: {optimal_workers/num_cpus:.1f}x)")
    print(f"   💾 RAM: Optimisée (GC désactivé)")
    print(f"   🎯 Target: Saturation CPU + I/O optimisé")
    print(f"   🔥 Mode: DEMON (priorité haute)\n")
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 3: Traitement parallèle DEMON MODE
    # ═══════════════════════════════════════════════════════════════
    print("⚡ [PHASE 3] Traitement DEMON en cours...\n")
    
    gc.disable()
    
    found_files = []
    error_files = []
    processed = 0
    found_count = 0
    
    try:
        with ProcessPoolExecutor(
            max_workers=optimal_workers,
            initializer=init_worker
        ) as executor:
            
            # Soumettre TOUS les jobs
            futures = {
                executor.submit(search_in_pdf_demon_mode, pdf): pdf
                for pdf in pdf_files
            }
            
            # Traitement temps réel avec timeout
            for future in as_completed(futures):
                processed += 1
                
                try:
                    pdf_path, page_num, found, error = future.result(timeout=60)
                    
                    if error:
                        error_files.append({'file': pdf_path, 'error': error})
                    elif found:
                        found_files.append({'file': pdf_path, 'page': page_num})
                        found_count += 1
                    
                    # Update toutes les 20 itérations
                    if processed % 20 == 0 or processed == total_files:
                        progress_bar_demon(processed, total_files, start_time, found_count)
                        
                except TimeoutError:
                    error_files.append({
                        'file': futures[future],
                        'error': 'Timeout (60s) - fichier trop volumineux ou corrompu'
                    })
                except Exception as e:
                    error_files.append({'file': futures[future], 'error': str(e)})
    
    finally:
        gc.enable()
    
    print("\n")
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 4: Écriture des résultats
    # ═══════════════════════════════════════════════════════════════
    print("💾 [PHASE 4] Écriture des résultats...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("╔" + "═" * 78 + "╗\n")
        f.write("║  🔥💀 RÉSULTATS DEMON MODE - Recherche 'Ventec' 💀🔥  " + " " * 19 + "║\n")
        f.write("╚" + "═" * 78 + "╝\n\n")
        
        f.write(f"📁 Dossier: {directory_path}\n")
        f.write(f"📊 Fichiers analysés: {total_files:,}\n")
        f.write(f"✅ Fichiers trouvés: {len(found_files):,}\n")
        f.write(f"❌ Erreurs: {len(error_files):,}\n")
        f.write(f"⚡ Vitesse: {total_files/(time.time()-start_time):.2f} PDF/s\n")
        f.write("─" * 80 + "\n\n")
        
        if found_files:
            f.write("🎯 FICHIERS CONTENANT 'VENTEC':\n")
            f.write("=" * 80 + "\n\n")
            for idx, result in enumerate(found_files, 1):
                f.write(f"{idx:5d}. 📄 {result['file']}\n")
                f.write(f"        └─ 📖 Page {result['page']}\n\n")
        else:
            f.write("❌ Aucun fichier contenant 'Ventec' trouvé.\n\n")
        
        if error_files:
            f.write("\n⚠️  ERREURS:\n")
            f.write("=" * 80 + "\n\n")
            for idx, result in enumerate(error_files, 1):
                f.write(f"{idx:4d}. ❌ {result['file']}\n")
                f.write(f"       └─ {result['error']}\n\n")
    
    # ═══════════════════════════════════════════════════════════════
    # STATISTIQUES FINALES
    # ═══════════════════════════════════════════════════════════════
    elapsed_time = time.time() - start_time
    avg_speed = total_files / elapsed_time
    success_rate = ((total_files - len(error_files)) / total_files * 100)
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + "🏆 TRAITEMENT TERMINÉ - STATISTIQUES DEMON MODE 🏆".center(80) + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    print(f"⏱️  Temps total: {elapsed_time:.2f}s ({elapsed_time/60:.2f} min)")
    print(f"⚡ Vitesse moyenne: {avg_speed:.2f} fichiers/seconde")
    print(f"🚀 Throughput: {total_files / (elapsed_time/60):.0f} fichiers/minute")
    print(f"📊 Taux de succès: {success_rate:.2f}%")
    print(f"")
    print(f"🎯 Résultats:")
    print(f"   ✅ Trouvés: {len(found_files):,} ({len(found_files)/total_files*100:.2f}%)")
    print(f"   ❌ Erreurs: {len(error_files):,} ({len(error_files)/total_files*100:.2f}%)")
    print(f"   ✔️  Succès: {total_files - len(error_files):,}")
    print(f"")
    print(f"💾 Résultats: {output_file}")
    print(f"🔥 CPU: {(optimal_workers/num_cpus)*100:.0f}% ({optimal_workers} workers)")
    print(f"💀 L'ordinateur a survécu... cette fois 💀\n")


if __name__ == "__main__":
    dossier_pdf = r"D:\Jabarout Leak\ATTESTATIONS"
    fichier_resultats = r"D:\Jabarout Leak\resultats_ventec_demon.txt"
    
    print(f"\n📁 Résultats: {fichier_resultats}\n")
    
    try:
        main(dossier_pdf, fichier_resultats)
    except KeyboardInterrupt:
        print("\n\n⚠️  Arrêt d'urgence!")
        gc.enable()
    except Exception as e:
        print(f"\n\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        gc.enable()
    finally:
        gc.enable()
