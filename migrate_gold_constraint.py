from database import get_connection

def add_gold_constraint():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if constraint already exists
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'gold_skill_counts' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name = 'gold_skill_counts_unique'
        """)
        
        if cursor.fetchone():
            print("✓ Constraint already exists - no action needed")
            conn.close()
            return
        
        # Add the unique constraint
        cursor.execute("""
            ALTER TABLE gold_skill_counts 
            ADD CONSTRAINT gold_skill_counts_unique 
            UNIQUE (skill, source, week_start)
        """)
        
        conn.commit()
        print("✓ Successfully added UNIQUE constraint to gold_skill_counts table")
        print("  Constraint: (skill, source, week_start)")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Error adding constraint: {e}")
        print("\nThis might mean you have duplicate rows. You may need to:")
        print("  1. Find duplicates: SELECT skill, source, week_start, COUNT(*) FROM gold_skill_counts GROUP BY skill, source, week_start HAVING COUNT(*) > 1")
        print("  2. Remove duplicates before adding the constraint")
    finally:
        conn.close()

if __name__ == "__main__":
    add_gold_constraint()
