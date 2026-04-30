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

def get_attendees():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        query = """
        SELECT a.attendeeID, a.attendeeName, c.companyName 
        FROM attendee a 
        JOIN company c ON a.attendeeCompanyID = c.companyID
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        print("\n--- Attendee List (MySQL) ---")
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]:<15} | Company: {row[2]}")
        conn.close()
    except Exception as e:
        print(f"MySQL Error: {e}")

def get_sessions():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT sessionID, sessionTitle, speakerName FROM session")
        rows = cursor.fetchall()
        print("\n--- Conference Sessions (MySQL) ---")
        for row in rows:
            print(f"ID: {row[0]} | Title: {row[1]:<35} | Speaker: {row[2]}")
        conn.close()
    except Exception as e:
        print(f"MySQL Error: {e}")

# --- NEO4J FUNCTIONS ---

def get_attendee_network():
    try:
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        with driver.session() as session:
            query = """
            MATCH (a:Attendee)-[r:CONNECTED_TO]->(b:Attendee)
            RETURN a.AttendeeID AS from_id, b.AttendeeID AS to_id
            LIMIT 20
            """
            result = session.run(query)
            print("\n--- Attendee Networking (Neo4j) ---")
            for record in result:
                print(f"Attendee {record['from_id']} is CONNECTED TO Attendee {record['to_id']}")
        driver.close()
    except Exception as e:
        print(f"Neo4j Error: {e}")
def get_rooms():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT roomName, capacity FROM room")
        rows = cursor.fetchall()
        print("\n--- Conference Rooms (MySQL) ---")
        for row in rows:
            print(f"Room: {row[0]:<20} | Capacity: {row[1]}")
        conn.close()
    except Exception as e:
        print(f"MySQL Error (Rooms): {e}")

# --- MAIN MENU ---

def main_menu():
    while True:
        print("\n" + "="*40)
        print("   CONFERENCE MANAGEMENT SYSTEM")
        print("="*40)
        print("1. View Attendees & Companies (SQL)")
        print("2. View Conference Sessions (SQL)")
        print("3. View Attendee Network (Neo4j)")
        print("4. View Conference Rooms (SQL)") # Nowa opcja
        print("0. Exit")
        
        choice = input("\nSelect an option: ")
        
        if choice == '1':
            get_attendees()
        elif choice == '2':
            get_sessions()
        elif choice == '3':
            get_attendee_network()
        elif choice == '4':
            get_rooms() # Wywołanie nowej funkcji
        elif choice == '0':
            print("Closing the application. Goodbye!")
            break
        else:
            print("Invalid selection, please try again.")

if __name__ == "__main__":
    main_menu()