from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Static + templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# Database connection function (IMPORTANT FIX)
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )


# Home page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Booking endpoint
@app.post("/book")
def book(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    check_in: str = Form(...),
    check_out: str = Form(...),
    room_type: str = Form(...),
    guests: int = Form(...),
    special_requests: str = Form(None)
):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO bookings
            (full_name, email, phone, check_in, check_out, room_type, guests, special_requests)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            full_name,
            email,
            phone,
            check_in,
            check_out,
            room_type,
            guests,
            special_requests
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

    finally:
        cursor.close()
        conn.close()


    return HTMLResponse("""
    <html>
        <head>
            <title>Booking Success</title>
            <style>
                body{
                    font-family: Arial;
                    background:#fdf2f8;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    height:100vh;
                }
                .box{
                    background:white;
                    padding:40px;
                    border-radius:20px;
                    text-align:center;
                    box-shadow:0 10px 25px rgba(0,0,0,0.1);
                }
                h1{
                    color:#db2777;
                }
                a{
                    text-decoration:none;
                    background:#ec4899;
                    color:white;
                    padding:12px 20px;
                    border-radius:10px;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>Booking Successful 💖</h1>
                <p>Your hotel room has been reserved.</p>
                <br><br>
                <a href="/">Go Back</a>
            </div>
        </body>
    </html>
    """)