import random
from datetime import date, timedelta
from app.data.database import Database

# Define 20 new clients
ADDITIONAL_CLIENTS = [
    ("Rohan Sen", "rohan@sensolutions.in", "9812345601", "Kolkata, West Bengal", "Sen Solutions", "E-learning design contracts"),
    ("Maya Rao", "maya@mayatech.com", "9812345602", "Bangalore, Karnataka", "Maya Tech", "SaaS platform optimization"),
    ("Kabir Dev", "kabir@devstudios.co", "9812345603", "Mumbai, Maharashtra", "Dev Studios", "Multimedia and VFX work"),
    ("Aisha Khan", "aisha@khanconsulting.com", "9812345604", "Hyderabad, Telangana", "Khan Consulting", "HR portal development"),
    ("Siddharth Roy", "siddharth@royals.in", "9812345605", "Pune, Maharashtra", "Roy Media", "Social media campaigns"),
    ("Neha Kapoor", "neha@kapoordesigns.com", "9812345606", "Delhi, NCR", "Kapoor Designs", "Graphic design projects"),
    ("Zoya Ali", "zoya@aliassociates.com", "9812345607", "Mumbai, Maharashtra", "Ali Associates", "Legal portal development"),
    ("Yash Vardhan", "yash@vardhancorp.in", "9812345608", "Jaipur, Rajasthan", "Vardhan Corp", "E-commerce expansion"),
    ("Divya Nair", "divya@nairgroup.co", "9812345609", "Kochi, Kerala", "Nair Group", "Branding deliverables"),
    ("Aditya Bose", "aditya@boseaudio.in", "9812345610", "Kolkata, West Bengal", "Bose Audio Lab", "Sound engineering projects"),
    ("Pooja Hegde", "pooja@hegdeconsult.com", "9812345611", "Bangalore, Karnataka", "Hegde Consulting", "IT infrastructure review"),
    ("Ranveer Gill", "ranveer@gillfarms.in", "9812345612", "Chandigarh, Punjab", "Gill Organic Farms", "Website creation"),
    ("Shreya Ghoshal", "shreya@ghoshalmedia.com", "9812345613", "Mumbai, Maharashtra", "Ghoshal Media", "Audio editing contracts"),
    ("Varun Dhawan", "varun@dhawanhub.in", "9812345614", "Pune, Maharashtra", "Dhawan Retail", "POS system development"),
    ("Tara Sutaria", "tara@tarafashion.com", "9812345615", "Mumbai, Maharashtra", "Tara Fashion House", "E-commerce platform"),
    ("Karthik Raja", "karthik@rajatech.in", "9812345616", "Chennai, Tamil Nadu", "Raja Tech Solutions", "Cloud migration project"),
    ("Rhea Chakraborty", "rhea@rheacreatives.co", "9812345617", "Bangalore, Karnataka", "Rhea Creatives", "Content localization"),
    ("Ishaan Khatter", "ishaan@khatterprod.in", "9812345618", "Mumbai, Maharashtra", "Khatter Productions", "Promotional animations"),
    ("Alia Bhatt", "alia@eternalsunshine.in", "9812345619", "Mumbai, Maharashtra", "Eternal Sunshine Prod", "UI design review"),
    ("Ranbir Kapoor", "ranbir@kapoorfilms.com", "9812345620", "Mumbai, Maharashtra", "Kapoor Films Ltd", "Custom software suite"),
]

PROJECT_TYPES = ["Design", "Video", "Writing", "Music", "Development"]
STATUS_OPTIONS = ["In Progress", "Completed", "Review", "Not Started"]

def main():
    db = Database()
    db.initialize()
    
    print(f"Adding 20 additional clients to the database...")
    today = date.today()
    
    for name, email, phone, address, company, notes in ADDITIONAL_CLIENTS:
        # Check if already added
        exists = db.execute("SELECT id FROM clients WHERE email = ?", (email,))
        if exists:
            continue
            
        # Insert client
        cid = db.execute_returning_id(
            "INSERT INTO clients (name, email, phone, address, company, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, address, company, notes),
        )
        
        # Add a random project for most of the new clients to make data rich
        if random.random() > 0.15:
            ptype = random.choice(PROJECT_TYPES)
            pstatus = random.choice(STATUS_OPTIONS)
            budget = random.randint(15, 95) * 5000
            deadline = (today + timedelta(days=random.randint(-15, 60))).isoformat()
            
            db.execute(
                "INSERT INTO projects (client_id, name, type, description, status, deadline, budget) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cid, f"{ptype} Project for {company}", ptype, f"Automatic project created for {company}", pstatus, deadline, budget)
            )

    print("[SUCCESS] 20 additional clients added successfully!")

if __name__ == "__main__":
    import random
    main()
