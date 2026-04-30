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
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT sessionTitle, speakerName FROM session")
        rows = cursor.fetchall()
        print("\n--- Speakers & Sessions ---")
        for row in rows:
            print(f"Speaker: {row[1]:<20} | Session: {row[0]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

def view_attendees_by_company():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        query = """
        SELECT a.attendeeName, c.companyName 
        FROM attendee a 
        JOIN company c ON a.attendeeCompanyID = c.companyID
        ORDER BY c.companyName
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        print("\n--- Attendees by Company ---")
        for row in rows:
            print(f"Company: {row[1]:<20} | Attendee: {row[0]}")
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

# --- PLACEHOLDERS FOR ADD FUNCTIONS (Will be implemented in next tasks) ---

def add_new_attendee():
    print("\n[INFO] 'Add New Attendee' functionality will be implemented soon.")

def add_attendee_connection():
    print("\n[INFO] 'Add Attendee Connection' functionality will be implemented soon.")

# --- MAIN MENU (Exactly as in Figure 2) ---

def main_menu():
    while True:
        print("\nConference Management")
        print("---------------------")
        print("\nMENU")
        print("====")
        print("1 – View Speakers & Sessions")
        print("2 – View Attendees by Company")
        print("3 – Add New Attendee")
        print("4 – View Connected Attendees")
        print("5 – Add Attendee Connection")
        print("6 – View Rooms")
        print("x – Exit application")
        
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