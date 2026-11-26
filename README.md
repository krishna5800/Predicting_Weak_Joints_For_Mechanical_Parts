# CAE Neural - Stress Analysis System with STEP Converter

A professional web-based application for predicting stress distribution on 3D CAD models using AI-powered neural networks. Features STEP/OFF file support, real-time 3D visualization, and HTML report export.

## Features

✅ **STEP to OFF Conversion** - Automatically converts CAD assembly files (STEP/STP) to mesh format (OFF)  
✅ **AI-Powered Stress Prediction** - Uses PointNet neural network for per-point stress analysis  
✅ **Interactive 3D Visualization** - Real-time Plotly visualization with stress heatmap and max stress highlighting  
✅ **HTML Report Export** - Download standalone HTML reports with embedded visualizations and metrics  
✅ **Drag & Drop Interface** - Intuitive dark-themed web UI for easy file uploads  
✅ **GPU Support** - Automatic CUDA detection for accelerated inference  

## Project Structure

```
d:\Predicting_Weak_Joints_With_CAE/
├── app.py                          # FastAPI backend with converter & prediction
├── converter.py                    # Standalone STEP→OFF conversion script
├── requirements.txt                # Python dependencies
├── model/
│   └── pointnet_cae_kaggle.pth     # Pre-trained PointNet model weights
├── templates/
│   └── index.html                  # Modern web UI (responsive & dark theme)
└── temp_files/                     # Auto-created temp directory for file processing
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- CUDA 11.8+ (optional, for GPU acceleration)

### Step 1: Install Dependencies
```bash
cd d:\Predicting_Weak_Joints_With_CAE
pip install -r requirements.txt
```

### Step 2: Verify Model File
Ensure `model/pointnet_cae_kaggle.pth` exists in the project directory.

### Step 3: Start the Server
```bash
python app.py
```

The application will be available at: **http://127.0.0.1:8000**

## Usage

### Web Interface

1. **Upload CAD Model**
   - Click or drag-drop a `.STEP`, `.STP`, or `.OFF` file
   - Files are automatically converted if needed
   - System shows "System Active" status when ready

2. **Run Analysis**
   - Click "Run Stress Analysis" button
   - Wait for "Analyzing Geometry..." overlay to complete
   - View 3D stress visualization with:
     - Color-coded stress values (Jet colorscale)
     - Max stress point highlighted with white diamond
     - Interactive 3D rotation/zoom controls

3. **Download Report**
   - Click "⬇ Download HTML Report" button
   - Standalone HTML file with:
     - Embedded Plotly 3D visualization
     - Stress metrics (min, max, average)
     - Analysis metadata and timestamp
     - Can be opened in any modern browser without server

4. **Upload Another File**
   - Click "Upload New File" to reset and analyze another model

## API Endpoints

### GET `/`
Returns the main web interface (index.html)

**Response:** HTML page

---

### POST `/predict`
Uploads and analyzes a CAD file (STEP or OFF)

**Request:**
```bash
Content-Type: multipart/form-data
Body: 
  - file: [binary file data]
```

**Response:**
```json
{
  "data": [/* Plotly trace data */],
  "layout": {/* Plotly layout config */},
  "stress_values": [array of float32 stress predictions],
  "original_filename": "model.step"
}
```

**Errors:**
```json
{
  "error": "STEP conversion failed: [error message]"
}
```

---

### POST `/export-html`
Generates a standalone HTML report with embedded visualization

**Request:**
```json
{
  "plot_json": {
    "data": [/* Plotly trace data */],
    "layout": {/* Plotly layout config */}
  },
  "stress_values": [array of stress values],
  "filename": "model.step"
}
```

**Response:** Binary HTML file download

## Processing Pipeline

### For STEP/STP Files:
1. **Upload** → Receive file
2. **GMSH Processing** → Load STEP file, generate 2D mesh, export to temporary STL
3. **Trimesh Bridge** → Load STL, export as OFF format
4. **Point Sampling** → Extract 4,096 surface points from mesh
5. **Normalization** → Center and scale point cloud
6. **Inference** → Run PointNet prediction on GPU/CPU
7. **Visualization** → Generate Plotly 3D scatter plot
8. **Cleanup** → Remove temporary files

### For OFF Files:
1. **Upload** → Direct mesh loading
2. **Skip to Step 4** (Point Sampling)

## Model Architecture

**PointNetDense** - Custom CNN-based architecture:
- Input: 3D point cloud (4096 points × 3 coordinates)
- 7-layer Conv1d with batch normalization
- Global max-pooling with feature concatenation
- Output: Per-point stress predictions (4096 × 1)
- Device: Auto-detect CUDA, fallback to CPU

## System Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.8+ |
| **RAM** | 8GB minimum (4GB model + 4GB processing) |
| **GPU** | Optional (NVIDIA CUDA 11.8+) |
| **Disk** | 2GB (model + dependencies) |
| **Browser** | Chrome/Edge/Firefox (Plotly support) |

## Configuration

### Environment Variables
Currently, no environment variables are required. All settings are hardcoded:
- **Model Path:** `model/pointnet_cae_kaggle.pth`
- **Server Host:** `127.0.0.1`
- **Server Port:** `8000`
- **Temp Directory:** `temp_files/`

### To Change Settings:
Edit `app.py` lines 29-33:
```python
MODEL_PATH = os.path.join("model", "pointnet_cae_kaggle.pth")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TEMP_DIR = "temp_files"
```

## Troubleshooting

### Issue: "Model not found"
**Solution:** Verify `model/pointnet_cae_kaggle.pth` exists and is readable

### Issue: STEP conversion fails
**Solution:** 
- Ensure GMSH is installed: `pip install gmsh`
- Verify STEP file is valid CAD format
- Try converting to STL first in your CAD software

### Issue: Out of memory during inference
**Solution:**
- Reduce batch size (currently processes one file at a time)
- Increase available system RAM
- Run on machine with GPU support

### Issue: Connection refused (cannot reach server)
**Solution:**
```bash
# Verify server is running
# Check: http://127.0.0.1:8000 in browser
# If down, restart:
python app.py
```

### Issue: CORS errors in browser console
**Solution:** CORS is already enabled in `app.py`. If issues persist, check browser security settings.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **fastapi** | ≥0.95.0 | Web framework |
| **uvicorn** | ≥0.20.0 | ASGI server |
| **torch** | ≥2.0.0 | Neural network inference |
| **numpy** | ≥1.21.0 | Numerical computation |
| **trimesh** | ≥3.9.0 | 3D mesh I/O and processing |
| **plotly** | ≥5.0.0 | Interactive 3D visualization |
| **gmsh** | ≥4.10.0 | STEP file conversion |
| **python-multipart** | ≥0.0.5 | File upload handling |
| **jinja2** | ≥3.0.0 | HTML templating |

## Performance Notes

- **STEP Conversion Time:** 2-10 seconds (depends on file complexity)
- **Mesh Processing:** 1-3 seconds (4,096 point sampling)
- **Inference Time:** 0.5-2 seconds (GPU: <0.5s, CPU: 1-2s)
- **Total Time:** 3-15 seconds per analysis
- **Output File Size:** HTML report ~5-10MB (includes Plotly visualization)

## Advanced Usage

### Batch Processing Script
```python
import requests

files = ['model1.step', 'model2.step', 'model3.off']

for file in files:
    with open(file, 'rb') as f:
        files_dict = {'file': f}
        response = requests.post('http://127.0.0.1:8000/predict', files=files_dict)
        result = response.json()
        
        if 'error' not in result:
            print(f"{file}: Max Stress = {max(result['stress_values']):.6f}")
        else:
            print(f"{file}: Error - {result['error']}")
```

### Standalone Converter
Use `converter.py` for STEP→OFF conversion without web interface:
```python
from converter import convert_step_to_off_locally

convert_step_to_off_locally(
    input_path="model.step",
    output_folder="./converted_models"
)
```

## Future Enhancements

- [ ] Batch file processing
- [ ] Result history/caching
- [ ] Custom mesh resolution options
- [ ] Export to CSV/JSON data format
- [ ] Model fine-tuning interface
- [ ] Docker containerization
- [ ] Multi-GPU support

## Support & Contributing

For issues or feature requests, please contact the development team.

## License

All rights reserved. Model weights are proprietary.

---

**Version:** 2.0 (STEP Converter + HTML Export)  
**Last Updated:** November 25, 2025  
**Status:** ✅ Production Ready
