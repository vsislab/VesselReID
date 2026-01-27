# VesselReID Dataset Downloader (Enhanced Fork)

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Academic%20Use-green.svg)]()

An enhanced, robust downloader for the VesselReID maritime vessel re-identification dataset. This fork adds significant reliability and performance improvements while maintaining full compatibility with the original dataset structure.

## ✨ Fork Enhancements

This enhanced downloader maintains full compatibility with the original VesselReID dataset while adding:

- **🔄 Intelligent File Skipping**: Automatically skips previously downloaded files
- **📡 Robust Retry Logic**: Exponential backoff retry mechanism for network instability
- **⚡ Concurrent Downloads**: Multi-threaded downloading with configurable worker count
- **📊 Progress Tracking**: Real-time progress bar with speed and ETA estimates
- **🛡️ Enhanced Error Handling**: Comprehensive error recovery and cleanup
- **⚙️ Flexible Configuration**: Command-line options for proxies, timeouts, and concurrency

## 📁 Dataset Introduction

The VesselReID dataset consists of 30,587 images of 1,248 vessels captured under various conditions (time, location, viewpoint, weather). Following standard re-ID dataset conventions:

- **Normal Split**: 624 vessel identities for training, 624 for testing
- **Extra Split**: 550 for training, 550 for testing, 148 for validation

For full details, see the original paper cited below.

## 📬 Dataset Availability

To obtain the VesselReID dataset for research purposes, contact:

**Email**: `info@vsislab.com`

Please include your full name and affiliation in your request. The dataset is provided for non-commercial research use only. You will receive the `VesselReID.json` annotation file required by this downloader.

## 🚀 Installation & Usage

### Installation

```bash
conda create -n vesselreid python=3.8
conda activate vesselreid
pip install -r requirements.txt
```

### Basic Usage
```bash
python downloader.py --pth '/path/to/VesselReID.json' --save_pth './datasets/VesselReID'
```

### Advanced Examples
```bash
# Faster downloading with 10 concurrent workers
python downloader.py --workers 10 --pth 'VesselReID.json' --save_pth './data'

# Use with SOCKS proxy and longer timeout
python downloader.py --proxy socks-client --timeout 60 --pth 'VesselReID.json'

# Resume interrupted download (skips existing files)
python downloader.py --resume --pth 'VesselReID.json' --save_pth './dataset'
```

### Command Line Arguments
Argument	Description	Default
--pth	Path to VesselReID.json annotation file	./VesselReID.json
--save_pth	Directory to save downloaded dataset	./VesselReID
--proxy	Proxy type: no, http, socks-client, socks-remote	no
--workers	Number of concurrent download workers	5
--timeout	Request timeout in seconds	30
--resume	Skip existing files (always enabled)	True

### 📋 Requirements
Python 3.6+

Standard library only (urllib, concurrent.futures, pathlib, etc.)

(Optional) requests if using alternative implementation

### 📄 Citation
If you use the VesselReID dataset in your research, please cite:

```
@ARTICLE{10046401,
  author={Zhang, Qian and Zhang, Mingxin and Liu, Jinghe and He, Xuanyu and Song, Ran and Zhang, Wei},
  journal={IEEE Transactions on Intelligent Transportation Systems}, 
  title={Unsupervised Maritime Vessel Re-Identification With Multi-Level Contrastive Learning}, 
  year={2023},
  volume={24},
  number={5},
  pages={5406-5418},
  doi={10.1109/TITS.2023.3243591}}
```

### 📝 Notes
This enhanced fork is compatible with the original VesselReID dataset structure

Download statistics are saved to download_stats.json in the output directory

The downloader automatically creates the necessary directory structure

All original dataset splits (normal and extra) are preserved

Maintains compatibility with the original VesselReID dataset while providing improved reliability and performance for research use.
