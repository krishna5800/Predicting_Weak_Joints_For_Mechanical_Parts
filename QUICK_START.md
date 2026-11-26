# 🚀 Quick Start Guide - CAE Neural Stress Analysis System

## 5-Minute Setup

### Step 1: Open Terminal
```bash
cd d:\Predicting_Weak_Joints_With_CAE
```

### Step 2: Start Server
```bash
python app.py
```

Expected output:
```
Loading model from model\pointnet_cae_kaggle.pth...
✅ Model loaded successfully!
Starting server at http://127.0.0.1:8000
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Open Browser
Navigate to: **http://127.0.0.1:8000**

You should see a dark-themed interface with "CAE NEURAL" branding and a file upload area.

---

## Using the Application

### Workflow 1: Analyze OFF File (Standard)
1. Click the upload area
2. Select a `.off` file
3. Click "Run Stress Analysis"
4. Wait for visualization to load (3-10 seconds)
5. View 3D stress map with colors
6. Explore with mouse:
   - **Left drag:** Rotate
   - **Right drag / Scroll:** Zoom
   - **Hover:** See stress values

### Workflow 2: Analyze STEP File (Automatic Conversion)
1. Click the upload area
2. Select a `.step` or `.stp` file
3. Click "Run Stress Analysis"
4. System automatically:
   - Converts STEP→OFF using GMSH
   - Samples 4,096 points
   - Runs stress prediction
   - Displays results
5. Same as Workflow 1 from here

### Workflow 3: Download HTML Report
1. After analysis is complete
2. Click "⬇ Download HTML Report" button
3. Browser downloads file: `{filename}_analysis_YYYYMMDD_HHMMSS.html`
4. Open HTML file in any browser
5. View professional report with:
   - Stress statistics (min, max, average)
   - Interactive 3D visualization
   - Analysis metadata
   - Timestamps

---

## Common Questions

### Q: Can I use both STEP and OFF files?
**A:** Yes! The system auto-detects the format:
- `.step` / `.stp` → Auto-converted to OFF
- `.off` → Used directly
- Just upload and it works!

### Q: What if conversion fails?
**A:** You'll see an error message. Possible causes:
- Invalid STEP file (corrupted or wrong format)
- Complex assembly with dependencies
- Try converting to STL in your CAD software first

### Q: How long does analysis take?
**A:** Typically 3-15 seconds:
- STEP conversion: 2-10s
- Processing: 1-3s
- Inference: <0.5s (GPU) or 1-2s (CPU)

### Q: What is the download file size?
**A:** HTML reports are typically 5-10MB (includes embedded Plotly visualization)

### Q: Can I batch process files?
**A:** Use the web interface for one file at a time, or see `README.md` for batch Python script

### Q: What if I need to restart?
**A:** Press `CTRL+C` in terminal to stop, then run `python app.py` again

---

## File Support Details

| Format | Extension | Status |
|--------|-----------|--------|
| Object File | `.off` | ✅ Direct support |
| STEP CAD | `.step` | ✅ Auto-convert |
| STEP CAD | `.stp` | ✅ Auto-convert |
| STL Mesh | `.stl` | ⚠️ Use OFF instead |
| OBJ Mesh | `.obj` | ⚠️ Use OFF instead |

---

## Output Files

### HTML Report Contents
```
📄 model_analysis_20251125_143022.html
├── Header Section
│   ├── Title: "◆ CAE ANALYSIS REPORT"
│   ├── Filename
│   └── Generation timestamp
│
├── Metrics Cards (Grid)
│   ├── Maximum Stress: [value]
│   ├── Minimum Stress: [value]
│   ├── Average Stress: [value]
│   └── Data Points: 4096
│
├── 3D Visualization
│   └── Interactive Plotly plot (rotatable/zoomable)
│
└── Footer
    └── Generation details
```

---

## Troubleshooting

### Issue: "Connection refused"
```
❌ Could not reach http://127.0.0.1:8000
```
**Solution:** 
1. Check if terminal shows server running
2. Make sure you ran `python app.py`
3. Wait 3-5 seconds after starting

### Issue: "Model not found"
```
❌ ERROR: Model not found at model\pointnet_cae_kaggle.pth
```
**Solution:**
1. Verify `model` folder exists
2. Verify `pointnet_cae_kaggle.pth` is inside `model` folder
3. Check file is not corrupted

### Issue: GMSH error
```
❌ STEP conversion failed: [error]
```
**Solution:**
1. Verify STEP file is valid (open in CAD software)
2. Try different STEP file
3. Check if gmsh installed: `pip list | grep gmsh`

### Issue: Out of memory
```
❌ MemoryError: ...
```
**Solution:**
1. Close other applications
2. Reduce parallel processing
3. Use GPU if available

---

## Advanced Usage

### Use GPU (Faster Inference)
Automatically detected! If NVIDIA GPU detected:
```
DEVICE = torch.device("cuda")  # Automatic
```
Results in <0.5s inference vs 1-2s on CPU

### Change Server Port
Edit `app.py` line 418:
```python
uvicorn.run(app, host="127.0.0.1", port=8000)  # Change 8000 to desired port
```

### Access from Another Computer
Edit `app.py` line 418:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Allow external access
```
Then access from: `http://<your-ip>:8000`

### API Usage (Python)
```python
import requests

# Upload and analyze
with open('model.step', 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:8000/predict',
        files={'file': f}
    )

result = response.json()
print(f"Max Stress: {max(result['stress_values'])}")
```

---

## System Information

After starting server, look for:

```
✅ Model loaded successfully!         # Model is ready
Running on http://127.0.0.1:8000      # Server is up
CUDA available                         # GPU will be used
```

---

## Next Steps

1. **Test with Sample Files**
   - Create or find `.step` or `.off` files
   - Upload and verify visualization

2. **Explore Reports**
   - Download HTML reports
   - Share with team
   - Compare results

3. **Read Full Documentation**
   - See `README.md` for comprehensive guide
   - See `IMPLEMENTATION_SUMMARY.md` for technical details

4. **Advanced Features**
   - See "Advanced Usage" section above
   - Modify threshold values
   - Integrate with other systems

---

## Support

For issues:
1. Check terminal output for error messages
2. Review troubleshooting section above
3. Verify all files are in correct locations
4. Check `README.md` for detailed docs

---

**Status: ✅ Ready to Use**

Start analyzing CAD models now! 🚀
