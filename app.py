import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import trimesh
import plotly.graph_objects as go
import json
import os
import shutil
import gmsh
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# --- 1. SETUP APP & PATHS ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Allow browser to talk to server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your model file
MODEL_PATH = os.path.join("model", "pointnet_cae_kaggle.pth")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- 2. MODEL ARCHITECTURE (From your Notebook) ---
class PointNetDense(nn.Module):
    def __init__(self):
        super(PointNetDense, self).__init__()
        self.conv1 = nn.Conv1d(3, 64, 1)
        self.conv2 = nn.Conv1d(64, 128, 1)
        self.conv3 = nn.Conv1d(128, 1024, 1)
        self.bn1 = nn.BatchNorm1d(64)
        self.bn2 = nn.BatchNorm1d(128)
        self.bn3 = nn.BatchNorm1d(1024)
        self.conv4 = nn.Conv1d(1088, 512, 1)
        self.conv5 = nn.Conv1d(512, 256, 1)
        self.conv6 = nn.Conv1d(256, 128, 1)
        self.conv7 = nn.Conv1d(128, 1, 1)
        self.bn4 = nn.BatchNorm1d(512)
        self.bn5 = nn.BatchNorm1d(256)
        self.bn6 = nn.BatchNorm1d(128)

    def forward(self, x):
        n_pts = x.size(2)
        x1 = F.relu(self.bn1(self.conv1(x)))
        x2 = F.relu(self.bn2(self.conv2(x1)))
        x3 = F.relu(self.bn3(self.conv3(x2)))
        gx = torch.max(x3, 2, keepdim=True)[0]
        gx = gx.repeat(1, 1, n_pts)
        concat = torch.cat([gx, x1], 1)
        x = F.relu(self.bn4(self.conv4(concat)))
        x = F.relu(self.bn5(self.conv5(x)))
        x = F.relu(self.bn6(self.conv6(x)))
        x = self.conv7(x)
        return x.transpose(2, 1)

# --- 3. LOAD THE MODEL ---
print(f"Loading model from {MODEL_PATH}...")
model = PointNetDense().to(DEVICE)

if os.path.exists(MODEL_PATH):
    # Load weights (handle CPU/GPU mapping automatically)
    state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(state_dict)
    model.eval()
    print("✅ Model loaded successfully!")
else:
    print(f"❌ ERROR: Model not found at {MODEL_PATH}. Please check folder structure.")

# --- 5. HELPER FUNCTIONS ---

def convert_step_to_off(input_path, output_folder=None):
    """Convert STEP file to OFF format using GMSH and Trimesh."""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File {input_path} not found.")
    
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, base_name + ".off")
    else:
        output_filename = os.path.splitext(input_path)[0] + ".off"
    
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    
    try:
        gmsh.merge(input_path)
        gmsh.model.mesh.generate(2)
        temp_stl = os.path.join(TEMP_DIR, f"temp_conversion_{datetime.now().timestamp()}.stl")
        gmsh.write(temp_stl)
        
        mesh = trimesh.load(temp_stl)
        mesh.export(output_filename)
        
        if os.path.exists(temp_stl):
            os.remove(temp_stl)
        
        return output_filename
    finally:
        gmsh.finalize()

def generate_html_report(filename, stress_values, plot_json):
    """Generate a standalone HTML file with embedded visualization and metadata."""
    max_stress = float(np.max(stress_values))
    min_stress = float(np.min(stress_values))
    avg_stress = float(np.mean(stress_values))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAE Analysis Report - {filename}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #f1f5f9;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(51, 65, 85, 0.5);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            color: #3b82f6;
            font-size: 28px;
        }}
        
        .header p {{
            margin: 5px 0;
            color: #94a3b8;
            font-size: 14px;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .metric-card {{
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            padding: 15px;
        }}
        
        .metric-card h3 {{
            margin: 0 0 8px 0;
            color: #94a3b8;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-card .value {{
            color: #3b82f6;
            font-size: 24px;
            font-weight: bold;
        }}
        
        .visualization {{
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(51, 65, 85, 0.5);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            height: 600px;
        }}
        
        #plotDiv {{
            width: 100%;
            height: 100%;
        }}
        
        .footer {{
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(51, 65, 85, 0.5);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            color: #64748b;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>◆ CAE ANALYSIS REPORT</h1>
            <p><strong>Filename:</strong> {filename}</p>
            <p><strong>Generated:</strong> {timestamp}</p>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Maximum Stress</h3>
                    <div class="value">{max_stress:.6f}</div>
                </div>
                <div class="metric-card">
                    <h3>Minimum Stress</h3>
                    <div class="value">{min_stress:.6f}</div>
                </div>
                <div class="metric-card">
                    <h3>Average Stress</h3>
                    <div class="value">{avg_stress:.6f}</div>
                </div>
                <div class="metric-card">
                    <h3>Data Points Analyzed</h3>
                    <div class="value">{len(stress_values)}</div>
                </div>
            </div>
        </div>
        
        <div class="visualization">
            <div id="plotDiv"></div>
        </div>
        
        <div class="footer">
            <p>This report was automatically generated by the CAE Analysis System.</p>
            <p>AI-powered stress prediction using PointNet neural network architecture.</p>
        </div>
    </div>
    
    <script>
        const plotData = {plot_json};
        Plotly.newPlot('plotDiv', plotData.data, plotData.layout, {{
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        }});
    </script>
</body>
</html>"""
    
    return html_content

# --- 6. ROUTES ---

@app.get("/")
def home(request: Request):
    """Serve the Frontend HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_stress(file: UploadFile = File(...)):
    """Handle file upload (STEP or OFF), run model, and return 3D plot JSON."""
    
    # Save file temporarily
    original_filename = file.filename
    file_ext = os.path.splitext(original_filename)[1].lower()
    temp_filename = os.path.join(TEMP_DIR, f"temp_{datetime.now().timestamp()}_{original_filename}")
    
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    converted_file = None
    try:
        # Convert STEP to OFF if needed
        if file_ext == ".step" or file_ext == ".stp":
            try:
                converted_file = convert_step_to_off(temp_filename, TEMP_DIR)
                mesh_file = converted_file
            except Exception as e:
                return {"error": f"STEP conversion failed: {str(e)}"}
        else:
            mesh_file = temp_filename
        
        # 1. Load Mesh
        mesh = trimesh.load(mesh_file)
        # Handle scene vs single mesh
        if isinstance(mesh, trimesh.Scene):
            if len(mesh.geometry) > 0:
                mesh = list(mesh.geometry.values())[0]
            else:
                return {"error": "Empty mesh file."}

        # 2. Preprocessing (Sample Points)
        num_points = 4096
        points, _ = trimesh.sample.sample_surface(mesh, num_points)
        points = np.array(points, dtype=np.float32)

        # 3. Normalize Data (Centering & Scaling)
        centroid = np.mean(points, axis=0)
        points_centered = points - centroid
        max_dist = np.max(np.linalg.norm(points_centered, axis=1))
        points_normalized = points_centered / max_dist

        # 4. Run Inference
        input_tensor = torch.tensor(points_normalized, dtype=torch.float32).transpose(0, 1).unsqueeze(0).to(DEVICE)
        
        with torch.no_grad():
            output = model(input_tensor)
        
        stress_values = output[0].cpu().numpy().flatten()

        # 5. Create Visualization (Plotly)
        fig = go.Figure(data=[go.Scatter3d(
            x=points_normalized[:, 0],
            y=points_normalized[:, 1],
            z=points_normalized[:, 2],
            mode='markers',
            marker=dict(
                size=3,
                color=stress_values,
                colorscale='Jet',
                opacity=0.8,
                colorbar=dict(title="Stress")
            ),
            text=[f"Stress: {s:.4f}" for s in stress_values],
            hoverinfo='text'
        )])

        # Highlight Max Stress Point
        max_idx = np.argmax(stress_values)
        fig.add_trace(go.Scatter3d(
            x=[points_normalized[max_idx, 0]],
            y=[points_normalized[max_idx, 1]],
            z=[points_normalized[max_idx, 2]],
            mode='markers',
            marker=dict(size=10, color='black', symbol='x'),
            name='Max Stress'
        ))

        fig.update_layout(
            title=f"Analysis Result: {original_filename}",
            scene=dict(
                xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            paper_bgcolor="#1e1e1e",
            font=dict(color="white")
        )

        plot_json = fig.to_json()
        
        # Store plot data and stress values in response
        response = json.loads(plot_json)
        response["stress_values"] = stress_values.tolist()
        response["original_filename"] = original_filename
        
        return response

    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}
    finally:
        # Cleanup temp files
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if converted_file and os.path.exists(converted_file):
            os.remove(converted_file)

@app.post("/export-html")
async def export_html(request: Request):
    """Generate and return a standalone HTML file with analysis report."""
    try:
        body = await request.json()
        plot_json = body.get("plot_json")
        stress_values = body.get("stress_values", [])
        filename = body.get("filename", "analysis.off")
        
        if not plot_json or not stress_values:
            return {"error": "Missing plot data or stress values"}
        
        stress_array = np.array(stress_values)
        html_content = generate_html_report(filename, stress_array, json.dumps(plot_json))
        
        # Generate filename for download
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(filename)[0]
        download_filename = f"{base_name}_analysis_{timestamp}.html"
        
        # Return as file download
        return StreamingResponse(
            iter([html_content]),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={download_filename}"}
        )
    except Exception as e:
        return {"error": f"HTML export failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    print("Starting server at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)