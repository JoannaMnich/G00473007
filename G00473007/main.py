import mysql.connector
from neo4j import GraphDatabase
import os

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

neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def view_connected_attendees():
    print("\nChoice: 4")
    attendee_id = input("Enter Attendee ID : ")

    try:
        # 1. Connect to MySQL and get the attendee name for the provided ID to display in the header
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Import attendee name based on the provided attendee ID to display it in the header
        cursor.execute("SELECT attendeeName FROM attendee WHERE attendeeID = %s", (attendee_id,))
        mysql_result = cursor.fetchone()

        if not mysql_result:
            print(f"*** ERROR *** Attendee ID: {attendee_id} does not exist in MySQL")
            conn.close()
            return

        attendee_name = mysql_result[0]
        print(f"Attendee Name: {attendee_name}")
        print("-" * 30)

        # 2. Check connections in Neo4j
        with neo4j_driver.session() as session:
            # Search for connections in both directions (-)
            query = """
            MATCH (a:Attendee {AttendeeID: $id})-[:CONNECTED_TO]-(connected)
            RETURN connected.AttendeeID AS id, connected.name AS name
            """
            # Convert to int because in Neo4j IDs are numbers
            neo4j_result = session.run(query, id=int(attendee_id))
            connections = list(neo4j_result)

            if connections:
                print("These attendees are connected:")
                for person in connections:
                    print(f"{person['id']}  |  {person['name']}")
            else:
                print("No connections")

        conn.close()

    except Exception as e:
        print(f"*** ERROR *** {e}")

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
    company_id = input("Enter Company ID : ")
    if not company_id.isdigit():
        print("Invalid input. Please enter a numeric Company ID.")
        return

    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()

        # Import company name based on the provided company ID to display it in the header
        cursor.execute("SELECT companyName FROM company WHERE companyID = %s", (company_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"No company found with ID {company_id}")
            return
            
        company_name = result[0]
        print(f"{company_name} Attendees")

        # Actualization of the query to include session date and room name, and to order results by session date
        query = """
        SELECT a.attendeeName, a.attendeeDOB, s.sessionTitle, sp.speakerName, s.sessionDate, r.roomName
        FROM attendee a
        JOIN attendee_session asen ON a.attendeeID = asen.attendeeID
        JOIN session s ON asen.sessionID = s.sessionID
        JOIN speaker sp ON s.speakerID = sp.speakerID
        JOIN room r ON s.roomID = r.roomID
        WHERE a.attendeeCompanyID = %s
        """
        cursor.execute(query, (company_id,))
        attendees = cursor.fetchall()

        if attendees:
           # Added session date column
            for row in attendees:
                print(f"{row[0]:<15} | {str(row[1]):<10} | {row[2]:<25} | {row[3]:<15} | {str(row[4]):<10} | {row[5]}")
        else:
            print(f"No attendees found for {company_name}")

        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

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
    print("\nChoice: 4")
    attendee_id = input("Enter Attendee ID : ").strip()
    if not attendee_id.isdigit():
        print("*** ERROR *** Invalid attendee ID")
        return
    
    try:
        # 1. Connect to MySQL
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        # Import the main attendee's name
        cursor.execute("SELECT attendeeName FROM attendee WHERE attendeeID = %s", (attendee_id,))
        mysql_result = cursor.fetchone()

        if not mysql_result:
            print(f"*** ERROR *** Attendee ID: {attendee_id} does not exist in MySQL")
            conn.close()
            return

        print(f"Attendee Name: {mysql_result[0]}")
        print("-" * 30)

        # 2. Import connections from Neo4j
        with neo4j_driver.session() as session:
            query = """
            MATCH (a:Attendee {AttendeeID: $id})-[:CONNECTED_TO]-(connected)
            RETURN connected.AttendeeID AS id
            """
            neo4j_result = session.run(query, id=int(attendee_id))
            ids = [record["id"] for record in neo4j_result]

            if ids:
                print("These attendees are connected:")
                for c_id in ids:
                    # Import the name of the connected attendee from MySQL, to avoid "None"
                    cursor.execute("SELECT attendeeName FROM attendee WHERE attendeeID = %s", (c_id,))
                    name_result = cursor.fetchone()
                    c_name = name_result[0] if name_result else "Unknown"
                    
                    print(f"{c_id}  |  {c_name}")
            else:
                print("No connections")

        conn.close()
    except Exception as e:
        print(f"*** ERROR *** {e}")

# --- PLACEHOLDERS FOR ADD FUNCTIONS  ---

def add_new_attendee():
    print("\nAdd New Attendee")
    print("----------------")
    
    try:
        attendee_id = input("Attendee ID : ").strip()
        name = input("Name : ").strip()
        dob = input("DOB : ").strip()
        gender = input("Gender : ").strip()
        
        # --- Check Gender ---
        if gender.lower() not in ["male", "female"]:
            print(f"*** ERROR *** Gender must be Male/Female")
            return # Pause function if gender is invalid
            
        company_id = input("Company ID : ").strip()

        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(buffered=True)

        # --- Check if Attendee ID already exists ---
        cursor.execute("SELECT attendeeID FROM attendee WHERE attendeeID = %s", (attendee_id,))
        if cursor.fetchone():
            print(f"*** ERROR *** Attendee ID: {attendee_id} already exists")
            conn.close()
            return # Pause function if ID already exists
        
        # --- Check if Company ID exists ---
        cursor.execute("SELECT companyID FROM company WHERE companyID = %s", (company_id,))
        if not cursor.fetchone():
            print(f"*** ERROR *** Company ID: {company_id} does not exist")
            conn.close()
            return
        
        query = """
        INSERT INTO attendee (attendeeID, attendeeName, attendeeDOB, attendeeGender, attendeeCompanyID)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (attendee_id, name, dob, gender, company_id)

        cursor.execute(query, values)
        conn.commit()

        print("\nAttendee successfully added")
        conn.close()

    except mysql.connector.Error as err:
        # Catch any MySQL errors and print them in a user-friendly way
        print(f"*** ERROR *** {err}")

def add_attendee_connection():
    print("\nChoice: 5")
    id1 = input("Enter Attendee 1 ID : ").strip()
    id2 = input("Enter Attendee 2 ID : ").strip()

    # validation to ensure both IDs are numeric before proceeding
    if not id1.isdigit() or not id2.isdigit():
        print("*** ERROR *** Invalid attendee ID")
        return

    try:
        # 1. Connect to MySQL and verify both attendee IDs exist, and get their names for Neo4j
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT attendeeID, attendeeName FROM attendee WHERE attendeeID IN (%s, %s)", (id1, id2))
        results = cursor.fetchall()

        if len(results) < 2:
            print("*** ERROR *** One or both Attendee IDs do not exist in MySQL")
            conn.close()
            return

        # Map the IDs to names for Neo4j
        names = {str(r[0]): r[1] for r in results}
        conn.close()

        # 2. Operations in Neo4j (MERGE creates a node if it doesn't exist, and a relationship only once)
        with neo4j_driver.session() as session:
            query = """
            MERGE (a:Attendee {AttendeeID: $id1}) ON CREATE SET a.name = $name1
            MERGE (b:Attendee {AttendeeID: $id2}) ON CREATE SET b.name = $name2
            MERGE (a)-[:CONNECTED_TO]->(b)
            """
            session.run(query, id1=int(id1), name1=names[id1], id2=int(id2), name2=names[id2])
            
            print(f"Attendee {id1} is now connected to Attendee {id2}")

    except Exception as e:
        print(f"*** ERROR *** {e}")

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
        print("x - Exit application")
        
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