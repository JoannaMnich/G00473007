import mysql.connector
from neo4j import GraphDatabase

# --- CONFIGURATION ---
mysql_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'database': 'appdbproj',
    'port': 3306
}

neo4j_uri = "bolt://127.0.0.1:7687"
neo4j_user = "neo4j"
neo4j_password = "password123"

# --- MYSQL FUNCTIONS ---

def view_speakers_and_sessions():
    try:
        # 1. Ask user for input 
        speaker_search = input("Enter speaker name : ").strip()
        
        print(f"Session Details For :  {speaker_search}")
        print("-" * 45) 
        
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # 2. Querry the database for speakers matching the input 
        # Search for the string anywhere in the speakerName0

        query = """
        SELECT s.speakerName, s.sessionTitle, r.roomName 
        FROM session s
        JOIN room r ON s.roomID = r.roomID
        WHERE s.speakerName LIKE %s
        ORDER BY s.speakerName ASC
        """

        search_term = f"%{speaker_search}%"
        cursor.execute(query, (search_term,))
        
        rows = cursor.fetchall()
        
        # 3. Check if any results were found and print them in a formatted way
        if not rows:
            print("No speakers found of that name")
        else:
            for row in rows:
                # Formatting matches the style in Figure 4
                print(f"{row[0]:<15} | {row[1]:<25} | {row[2]}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def view_attendees_by_company():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # 1. Validation Loop 
        while True:
            company_id_input = input("Enter Company ID : ").strip()
            if company_id_input.isdigit() and int(company_id_input) > 0:
                company_id = int(company_id_input)
                break
            # If input is invalid, show error and prompt again
            print("Invalid input. Please enter a positive integer for Company ID.")

        # 2. Check if company exists 
        cursor.execute("SELECT companyName FROM company WHERE companyID = %s", (company_id,))
        company_row = cursor.fetchone()

        if not company_row:
            print(f"Company with ID {company_id} doesn't exist")
            conn.close()
            return

        company_name = company_row[0]
        print(f"\n{company_name} Attendees")
        print("-" * 30)

        # 3. Main Query
        query = """
        SELECT a.attendeeName, a.attendeeDOB, s.sessionTitle, s.speakerName, s.sessionDate, r.roomName
        FROM attendee a
        JOIN registration reg ON a.attendeeID = reg.attendeeID
        JOIN session s ON reg.sessionID = s.sessionID
        JOIN room r ON s.roomID = r.roomID
        WHERE a.attendeeCompanyID = %s
        ORDER BY a.attendeeName ASC
        """
        
        cursor.execute(query, (company_id,))
        rows = cursor.fetchall()

        # 4. Handle company with no attendees 
        if not rows:
            print(f"No attendees found for  {company_name}")
        else:
            for row in rows:
                print(f"{row[0]:<12} | {row[1]} | {row[2]:<25} | {row[3]:<15} | {row[4]} | {row[5]}")

        conn.close()
    except Exception as e:
        print(f"Error: {e}")


def view_rooms():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT roomName, capacity FROM room")
        rows = cursor.fetchall()
        print("\n--- Conference Rooms ---")
        for row in rows:
            print(f"Room: {row[0]:<20} | Capacity: {row[1]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

# --- NEO4J FUNCTIONS ---

def view_connected_attendees():
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        with driver.session() as session:
            query = "MATCH (a:Attendee)-[:CONNECTED_TO]->(b:Attendee) RETURN a.AttendeeID, b.AttendeeID"
            result = session.run(query)
            print("\n--- Connected Attendees ---")
            for record in result:
                print(f"Attendee {record[0]} <-> Attendee {record[1]}")
        driver.close()
    except Exception as e:
        print(f"Error: {e}")

# --- PLACEHOLDERS FOR ADD FUNCTIONS  ---

def add_new_attendee():
    print("\nAdd New Attendee")
    print("----------------")
    
    # 1. Ask user for input for the new attendee's details (ID, name, etc.)
    try:
        attendee_id = input("Attendee ID : ").strip()
        name = input("Name : ").strip()
        dob = input("DOB : ").strip()
        gender = input("Gender : ").strip()
        company_id = input("Company ID : ").strip()

        # 2. Connection to MySQL and insert the new attendee into the database
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO attendee (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (attendee_id, name, dob, gender, company_id)

        cursor.execute(query, values)
        
        # Commit aproving the transaction to save changes to the database
        conn.commit()

        print("\nAttendee successfully added")
        
        conn.close()
    except mysql.connector.Error as err:
        # If there's an error related to MySQL (like duplicate ID, foreign key constraint, etc.), it will be caught here
        print(f"Error: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def add_attendee_connection():
    print("\n[INFO] 'Add Attendee Connection' functionality will be implemented soon.")

# --- MAIN MENU  ---

def main_menu():
    while True:
        print("\nConference Management")
        print("---------------------")
        print("\nMENU")
        print("====")
        print("1 - View Speakers & Sessions")
        print("2 - View Attendees by Company")
        print("3 - Add New Attendee")
        print("4 - View Connected Attendees")
        print("5 - Add Attendee Connection")
        print("6 - View Rooms")
        print("x -Exit application")
        
        choice = input("Choice: ").strip().lower()
        
        if choice == '1':
            view_speakers_and_sessions()
        elif choice == '2':
            view_attendees_by_company()
        elif choice == '3':
            add_new_attendee()
        elif choice == '4':
            view_connected_attendees()
        elif choice == '5':
            add_attendee_connection()
        elif choice == '6':
            view_rooms()
        elif choice == 'x':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()