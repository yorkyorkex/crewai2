from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv

from travel_planner2.crew import TravelPlanner2

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Travel Planner API",
    description="AI-powered travel planning service using CrewAI",
    version="1.0.0"
)

# Request models
class TravelPlanRequest(BaseModel):
    destination: str = Field(..., description="Travel destination (city, country)")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD format)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD format)")
    days: Optional[int] = Field(None, ge=1, le=14, description="Number of days for the trip (1-14 days)")
    preferences: Optional[str] = Field(None, description="Special preferences or requirements")

class PlanResponse(BaseModel):
    destination: str
    start_date: Optional[str]
    end_date: Optional[str]
    days: int
    plan: str

class HealthResponse(BaseModel):
    ok: bool

# Remove old storage system - not needed anymore

@app.get("/", response_class=HTMLResponse)
async def home():
    """Travel planner web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌍 AI Travel Planner</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 600px;
                width: 100%;
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #555;
                font-size: 1.1em;
            }
            input, textarea, select {
                width: 100%;
                padding: 15px;
                border: 2px solid #e1e1e1;
                border-radius: 10px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            input:focus, textarea:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            .date-group {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            .or-divider {
                text-align: center;
                margin: 20px 0;
                position: relative;
                color: #888;
            }
            .or-divider::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 0;
                right: 0;
                height: 1px;
                background: #e1e1e1;
                z-index: 1;
            }
            .or-divider span {
                background: white;
                padding: 0 20px;
                position: relative;
                z-index: 2;
            }
            .submit-btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 18px 40px;
                border: none;
                border-radius: 50px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s;
            }
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            .submit-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .loading {
                display: none;
                text-align: center;
                margin-top: 20px;
                color: #667eea;
            }
            .api-links {
                text-align: center;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e1e1e1;
            }
            .api-links a {
                color: #667eea;
                text-decoration: none;
                margin: 0 15px;
                font-weight: 500;
            }
            .api-links a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 AI Travel Planner</h1>
            <form id="travelForm" action="/plan-web" method="post">
                <div class="form-group">
                    <label for="destination">📍 Destination *</label>
                    <input type="text" id="destination" name="destination" placeholder="e.g. Tokyo, Japan or Paris, France" required>
                </div>

                <div class="date-group">
                    <div class="form-group">
                        <label for="start_date">📅 Start Date *</label>
                        <input type="date" id="start_date" name="start_date" required>
                    </div>
                    <div class="form-group">
                        <label for="days">🗓️ Days *</label>
                        <select id="days" name="days" required>
                            <option value="">Select days...</option>
                            <option value="1">1 day</option>
                            <option value="2">2 days</option>
                            <option value="3">3 days</option>
                            <option value="4">4 days</option>
                            <option value="5">5 days</option>
                            <option value="6">6 days</option>
                            <option value="7">7 days</option>
                            <option value="10">10 days</option>
                            <option value="14">14 days</option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label for="preferences">💭 Preferences (Optional)</label>
                    <textarea id="preferences" name="preferences" rows="3" placeholder="e.g. museums, food, history, shopping..."></textarea>
                </div>

                <button type="submit" class="submit-btn" id="submitBtn">
                    🚀 Create Travel Plan
                </button>
            </form>

            <div class="loading" id="loading">
                <p>🤖 AI is creating your personalized travel plan...</p>
                <p>⏳ This may take 30-60 seconds</p>
            </div>

            <div class="api-links">
                <a href="/docs">📖 API Docs</a>
                <a href="/health">💚 Health Check</a>
            </div>
        </div>

        <script>
            document.getElementById('travelForm').addEventListener('submit', function(e) {
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');

                submitBtn.disabled = true;
                submitBtn.textContent = '🤖 AI Working...';
                loading.style.display = 'block';
            });
        </script>
    </body>
    </html>
    """

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(ok=True)

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Simple test page"""
    return """<!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
    </head>
    <body>
        <h1>🚀 Test Page Working!</h1>
        <p>Server is running correctly on port 8003</p>
        <p><a href="/">Go to Travel Planner</a></p>
    </body>
    </html>"""

@app.post("/plan", response_model=PlanResponse)
async def create_travel_plan(request: TravelPlanRequest):
    """
    Create a new travel plan

    Input: JSON with destination, start_date?, end_date?, days?
    Output: JSON with destination, start_date, end_date, days, plan (Markdown)
    """
    # For demo purposes, we'll generate a mock response without API keys
    # In production, you would need: OPENAI_API_KEY, SERPER_API_KEY, GOOGLE_MAPS_API_KEY
    required_env_vars = ["OPENAI_API_KEY", "SERPER_API_KEY", "GOOGLE_MAPS_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        # Generate mock response for demo
        days_for_demo = request.days if request.days else 3
        mock_plan = f"""# {days_for_demo}-Day Travel Plan for {request.destination}

## Day 1
**Morning (9:00 AM)**
- Visit famous attraction (Searcher Agent found this using Serper API)
- Travel time: 15 minutes (Planner Agent calculated using Google Maps)

**Afternoon (1:00 PM)**
- Lunch at local restaurant (Searcher Agent found this using Google Maps Places)
- Visit cultural site (2:30 PM)

**Evening (6:00 PM)**
- Dinner at recommended restaurant

## Day 2
**Morning (9:00 AM)**
- Museum visit
- Travel time optimized by Planner Agent

**Afternoon (2:00 PM)**
- Shopping district
- Optimal route planned with Google Maps Directions API

## Day 3
**Morning (10:00 AM)**
- Final sightseeing
- Return journey planned

---
*This travel plan was generated by:*
- **Searcher Agent**: Used Serper API & Google Maps Places API
- **Planner Agent**: Used Google Maps Directions & Distance Matrix API
- **Reporter Agent**: Used OpenAI GPT-4o-mini for formatting

*Note: This is a demo response. Set API keys for full functionality.*
"""

        # Calculate dates for demo
        if request.start_date:
            start_date_demo = request.start_date
            if request.end_date:
                end_date_demo = request.end_date
            else:
                from datetime import datetime as dt, timedelta
                start = dt.strptime(request.start_date, "%Y-%m-%d")
                end = start + timedelta(days=days_for_demo-1)
                end_date_demo = end.strftime("%Y-%m-%d")
        else:
            start_date_demo = None
            end_date_demo = None

        return PlanResponse(
            destination=request.destination,
            start_date=start_date_demo,
            end_date=end_date_demo,
            days=days_for_demo,
            plan=mock_plan
        )

    # Calculate days from dates or use provided days
    if request.start_date and request.end_date:
        from datetime import datetime as dt
        start = dt.strptime(request.start_date, "%Y-%m-%d")
        end = dt.strptime(request.end_date, "%Y-%m-%d")
        calculated_days = (end - start).days + 1

        if request.days and request.days != calculated_days:
            raise HTTPException(
                status_code=400,
                detail=f"Days parameter ({request.days}) doesn't match date range ({calculated_days} days)"
            )

        days = calculated_days
        start_date = request.start_date
        end_date = request.end_date
    elif request.days:
        days = request.days
        if request.start_date:
            from datetime import datetime as dt, timedelta
            start = dt.strptime(request.start_date, "%Y-%m-%d")
            end = start + timedelta(days=days-1)
            start_date = request.start_date
            end_date = end.strftime("%Y-%m-%d")
        else:
            start_date = None
            end_date = None
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'days' or both 'start_date' and 'end_date'"
        )

    try:
        # Prepare inputs for the crew
        inputs = {
            "destination": request.destination,
            "duration": days
        }

        # Add preferences if provided
        if request.preferences:
            inputs["preferences"] = request.preferences

        # Run the CrewAI crew synchronously
        crew = TravelPlanner2().crew()
        result = crew.kickoff(inputs=inputs)

        return PlanResponse(
            destination=request.destination,
            start_date=start_date,
            end_date=end_date,
            days=days,
            plan=str(result)
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in create_travel_plan: {str(e)}")
        print(f"Full traceback: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating travel plan: {str(e)}"
        )

@app.post("/plan-file")
async def create_travel_plan_file(request: TravelPlanRequest):
    """
    Create a travel plan and return as downloadable Markdown file

    Input: JSON with destination, start_date?, end_date?, days?
    Output: Markdown file download
    """
    # Validate environment variables
    required_env_vars = ["OPENAI_API_KEY", "SERPER_API_KEY", "GOOGLE_MAPS_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        raise HTTPException(
            status_code=500,
            detail=f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    # Calculate days from dates or use provided days
    if request.start_date and request.end_date:
        from datetime import datetime as dt
        start = dt.strptime(request.start_date, "%Y-%m-%d")
        end = dt.strptime(request.end_date, "%Y-%m-%d")
        calculated_days = (end - start).days + 1

        if request.days and request.days != calculated_days:
            raise HTTPException(
                status_code=400,
                detail=f"Days parameter ({request.days}) doesn't match date range ({calculated_days} days)"
            )

        days = calculated_days
    elif request.days:
        days = request.days
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'days' or both 'start_date' and 'end_date'"
        )

    try:
        # Prepare inputs for the crew
        inputs = {
            "destination": request.destination,
            "duration": days
        }

        # Add preferences if provided
        if request.preferences:
            inputs["preferences"] = request.preferences

        # Run the CrewAI crew synchronously
        crew = TravelPlanner2().crew()
        result = crew.kickoff(inputs=inputs)

        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(str(result))
            temp_file_path = temp_file.name

        # Generate filename
        safe_destination = "".join(c for c in request.destination if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_destination}_{days}days_travel_plan.md"

        return FileResponse(
            path=temp_file_path,
            filename=filename,
            media_type='text/markdown'
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating travel plan: {str(e)}"
        )

@app.post("/plan-web", response_class=HTMLResponse)
async def create_travel_plan_web(
    destination: str = Form(...),
    start_date: str = Form(...),
    days: str = Form(...),
    preferences: Optional[str] = Form(None)
):
    """
    Handle web form submission and return HTML result page
    """
    # Validate environment variables
    required_env_vars = ["OPENAI_API_KEY", "SERPER_API_KEY", "GOOGLE_MAPS_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        return f"""
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>❌ Configuration Error</h1>
        <p>Missing required environment variables: {', '.join(missing_vars)}</p>
        <a href="/">← Back to Home</a>
        </body></html>
        """

    try:
        # Simple validation and conversion
        final_days = int(days)
        final_start_date = start_date

        # Calculate end date
        from datetime import datetime as dt, timedelta
        start = dt.strptime(start_date, "%Y-%m-%d")
        end = start + timedelta(days=final_days-1)
        final_end_date = end.strftime("%Y-%m-%d")

        # Prepare inputs for the crew
        inputs = {
            "destination": destination,
            "duration": final_days
        }

        # Add preferences if provided
        if preferences and preferences.strip():
            inputs["preferences"] = preferences

        # Run the CrewAI crew
        crew = TravelPlanner2().crew()
        result = crew.kickoff(inputs=inputs)

        # Convert Markdown to HTML-friendly format
        import html
        markdown_content = str(result)
        html_content = html.escape(markdown_content)

        # Simple markdown to HTML conversion
        html_content = html_content.replace('\\n', '\n')
        lines = html_content.split('\n')
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                formatted_lines.append(f'<h1>{line[2:]}</h1>')
            elif line.startswith('## '):
                formatted_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('### '):
                formatted_lines.append(f'<h3>{line[4:]}</h3>')
            elif line.startswith('- '):
                formatted_lines.append(f'<li>{line[2:]}</li>')
            elif line.startswith('**') and line.endswith('**'):
                formatted_lines.append(f'<p><strong>{line[2:-2]}</strong></p>')
            elif line:
                formatted_lines.append(f'<p>{line}</p>')
            else:
                formatted_lines.append('<br>')

        formatted_content = '\n'.join(formatted_lines)

        # Return HTML result page
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🌍 Your Travel Plan - {destination}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    background: white;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #f0f0f0;
                }}
                .trip-info {{
                    background: #f8f9ff;
                    padding: 20px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .content {{
                    margin-bottom: 30px;
                }}
                h1 {{ color: #333; font-size: 2.5em; margin: 0; }}
                h2 {{ color: #667eea; border-bottom: 2px solid #e1e1e1; padding-bottom: 10px; }}
                h3 {{ color: #555; }}
                p {{ margin: 10px 0; }}
                li {{ margin: 5px 0; }}
                .actions {{
                    text-align: center;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 2px solid #f0f0f0;
                }}
                .btn {{
                    display: inline-block;
                    padding: 15px 30px;
                    margin: 10px;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: 600;
                    transition: transform 0.2s;
                }}
                .btn:hover {{ transform: translateY(-2px); }}
                .btn-primary {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .btn-secondary {{
                    background: #f8f9ff;
                    color: #667eea;
                    border: 2px solid #667eea;
                }}
                .download-info {{
                    background: #e8f5e8;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    text-align: center;
                    color: #2d5a2d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌍 Your Travel Plan</h1>
                </div>

                <div class="trip-info">
                    <h2>📍 {destination}</h2>
                    <p><strong>🗓️ Duration:</strong> {final_days} days</p>
                    {f'<p><strong>📅 Dates:</strong> {final_start_date} to {final_end_date}</p>' if final_start_date else ''}
                    {f'<p><strong>💭 Preferences:</strong> {preferences}</p>' if preferences and preferences.strip() else ''}
                </div>

                <div class="content">
                    {formatted_content}
                </div>

                <div class="actions">
                    <a href="/" class="btn btn-primary">🏠 Plan Another Trip</a>
                    <form style="display: inline;" action="/plan-file" method="post">
                        <input type="hidden" name="destination" value="{destination}">
                        <input type="hidden" name="days" value="{final_days}">
                        {f'<input type="hidden" name="start_date" value="{final_start_date}">' if final_start_date else ''}
                        {f'<input type="hidden" name="end_date" value="{final_end_date}">' if final_end_date else ''}
                        {f'<input type="hidden" name="preferences" value="{preferences}">' if preferences and preferences.strip() else ''}
                        <button type="submit" class="btn btn-secondary">📁 Download as File</button>
                    </form>
                </div>

                <div class="download-info">
                    <p>💡 Tip: You can download this plan as a Markdown file to save or share!</p>
                </div>
            </div>
        </body>
        </html>
        """

    except Exception as e:
        return f"""
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>❌ Error</h1>
        <p>Error generating travel plan: {str(e)}</p>
        <a href="/">← Back to Home</a>
        </body></html>
        """

# Old endpoints removed - using direct synchronous responses now

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)