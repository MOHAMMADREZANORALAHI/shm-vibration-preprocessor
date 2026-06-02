# SHM Vibration Preprocessor Toolkit

**Advanced Signal Processing Tools for Structural Health Monitoring (SHM)**

A comprehensive Python toolkit for vibration data preprocessing, analysis, and feature extraction in Structural Health Monitoring applications, particularly for cantilever beam impact tests and modal analysis.

## ✨ Features

- **Data Cropping Tool**: Crop vibration signals based on time windows
- **Multi-Directional Plotter**: Interactive time-history plots with impact detection
- **Advanced Preprocessing Dashboard**: Detrending, bandpass filtering, normalization
- **FDD Modal Analysis**: Frequency Domain Decomposition for natural frequency identification
- **Batch Feature Extractor**: Statistical & frequency-domain feature extraction with FFT

## 🛠️ Tools Included

| Tool | Description | GUI |
|------|-------------|-----|
| `crop_vibration.py` | Time-based signal cropping | ✅ |
| `plot_vibration.py` | Multi-axis interactive plotting | ✅ |
| `shm_advanced_dashboard.py` | Advanced filtering & preprocessing | ✅ |
| `shm_fdd_batch_analyzer.py` | Operational Modal Analysis (FDD) | ✅ |
| `shm_feature_extractor.py` | Feature extraction + FFT | ✅ |

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/MOHAMMADREZANORALAHI/shm-vibration-preprocessor.git
cd shm-vibration-preprocessor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run tools (Windows)
Double-click any `.bat` file:
- `crop-vibration.bat`
- `plot-vibration.BAT`
- `shm_advanced_dashboard.bat`
- etc.

## 📁 Project Structure

```
shm-vibration-preprocessor/
├── scripts/           # Main Python tools
├── tools/             # Windows batch launchers
├── docs/              # Documentation
├── examples/          # Sample data (soon)
├── screenshots/       # GUI screenshots
├── README.md
└── requirements.txt
```

## 🧪 Dependencies
- pandas
- numpy
- matplotlib
- scipy
- tkinter (built-in)

## 📄 License
MIT License - Feel free to use and modify for research and academic purposes.

---

**Developed for Structural Health Monitoring Research**  
**Cantilever Beam Impact Testing**