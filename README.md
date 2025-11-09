PDF-Turbo-Scan
Ultra-fast, parallel PDF keyword search for massive folders—scan thousands of PDFs in seconds.

🚀 Features
Search for any text or phrase across tens of thousands of PDFs at once

Leverages all CPU cores (up to 200+ workers)

Binary scan optimization for lightning speed

Blazing performance: up to 300 PDFs per second (depends on disk/CPU)

Detailed real-time progress and error handling

Compatible with Windows and Linux

🔧 Requirements
Python 3.8+

PyMuPDF (pip install pymupdf)

psutil (pip install psutil)

SSD or NVMe recommended for best performance

📦 Installation
Clone the repository and install dependencies:

bash
git clone https://github.com/tahabicho/PDF-Turbo-Scan.git
cd PDF-Turbo-Scan
pip install pymupdf psutil
⚡ Usage
Edit SEARCH_STR inside the script to set your search keyword.
Configure your input folder and output file:

python
dossier = r"E:\\Jabarout Leak\\ATTESTATIONS"
output = r"E:\\Jabarout Leak\\resultats_APOCALYPSE.txt"
Run the search:

bash
python turbo_pdf_scan.py
Results will be saved in your specified output file.

📝 Example Output
text
💀☠️ APOCALYPSE MODE RESULTS ☠️💀
Total: 53,400
Found: 1,024
Errors: 12

FILES FOUND:
================================================================================
1. E:\Jabarout Leak\ATTESTATIONS\a201.pdf (page 3)
2. E:\Jabarout Leak\ATTESTATIONS\c332.pdf (page 7)
...
💡 Performance Tips
Use NVMe SSD/RAMDisk for maximum speed

Temporarily disable antivirus and system indexing

For monster performance, split your workload over multiple servers
