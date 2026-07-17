import os
import csv
from io import StringIO
from flask import Flask, render_template, jsonify, Response, request
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

app = Flask(__name__)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: SUPABASE_URL and SUPABASE_KEY are not set in .env")
    supabase = None
else:
    supabase: Client = create_client(url, key)

@app.route("/")
def index():
    # Render the main dashboard template
    return render_template("index.html")

@app.route("/api/data")
def api_data():
    if not supabase:
        return jsonify({"error": "Supabase client not initialized"}), 500

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    # Query supabase
    query = supabase.table("temperature_readings").select("*").order("date", desc=True).order("time", desc=True)
    
    # Apply date filters if provided
    if start_date:
        query = query.gte("date", start_date)
    if end_date:
        query = query.lte("date", end_date)
        
    # Limit to latest 100 for API polling if no date range is provided
    if not start_date and not end_date:
        query = query.limit(100)
        
    try:
        response = query.execute()
        data = response.data
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/export")
def export_csv():
    if not supabase:
        return "Supabase client not initialized", 500

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    query = supabase.table("temperature_readings").select("*").order("date", desc=True).order("time", desc=True)
    
    if start_date:
        query = query.gte("date", start_date)
    if end_date:
        query = query.lte("date", end_date)
        
    try:
        response = query.execute()
        data = response.data
        
        si = StringIO()
        cw = csv.writer(si)
        # Write CSV Headers
        cw.writerow(["ID", "Temperature", "Date", "Time", "Created At"])
        
        # Write rows
        for row in data:
            cw.writerow([
                row.get("id", ""), 
                row.get("temperature", ""), 
                row.get("date", ""), 
                row.get("time", ""), 
                row.get("created_at", "")
            ])
            
        output = Response(si.getvalue(), mimetype="text/csv")
        output.headers["Content-Disposition"] = "attachment; filename=temperature_data.csv"
        return output
    except Exception as e:
        return f"Error exporting data: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
