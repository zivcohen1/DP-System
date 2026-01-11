from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import sys
import os

# Add parent directory to path to import dp.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dp import DPDSLRewriter, DPDSLConfig

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

# Initialize rewriter
config = DPDSLConfig()
rewriter = None

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_rewriter():
    """Initialize the DP rewriter with database connection"""
    global rewriter
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    rewriter = DPDSLRewriter(conn, config)
    print("✅ DP Rewriter initialized")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a DP query"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        user_id = data.get('user_id', 'default_user')
        
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        # Execute query through DP rewriter
        result, error = rewriter.execute_query(query, user_id, verbose=True)
        
        if error:
            return jsonify({
                'success': False,
                'error': error,
                'budget': rewriter.get_user_budget_status(user_id)
            }), 200
        
        # Convert result to list of dicts
        if result and len(result) > 0:
            # Get column names - use simple generic names
            if isinstance(result[0], tuple):
                num_cols = len(result[0])
                if num_cols == 1:
                    columns = ['result']
                else:
                    columns = [f'column_{i}' for i in range(num_cols)]
            else:
                columns = ['result']
            
            result_list = [dict(zip(columns, row if isinstance(row, tuple) else [row])) for row in result]
        else:
            result_list = []
        
        return jsonify({
            'success': True,
            'data': result_list,
            'row_count': len(result_list),
            'budget': rewriter.get_user_budget_status(user_id)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/budget/<user_id>', methods=['GET'])
def get_budget(user_id):
    """Get budget status for a user"""
    try:
        budget_status = rewriter.get_user_budget_status(user_id)
        return jsonify(budget_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/budget/<user_id>/reset', methods=['POST'])
def reset_budget(user_id):
    """Reset budget for a user"""
    try:
        rewriter.reset_user_budget(user_id)
        budget_status = rewriter.get_user_budget_status(user_id)
        return jsonify({
            'success': True,
            'message': f'Budget reset for user {user_id}',
            'budget': budget_status
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/budget/<user_id>/history', methods=['GET'])
def get_budget_history(user_id):
    """Get budget usage history for a user"""
    try:
        budget_status = rewriter.get_user_budget_status(user_id)
        # Get query history from budget manager
        history = budget_status.get('queries', [])
        return jsonify({
            'user_id': user_id,
            'history': history,
            'total_spent': budget_status.get('spent', 0),
            'remaining': budget_status.get('remaining', budget_status.get('max', 10.0))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables', methods=['GET'])
def get_tables():
    """Get list of available tables with details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        table_names = [row[0] for row in cursor.fetchall()]
        
        tables_info = []
        for table_name in table_names:
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            tables_info.append({
                'name': table_name,
                'columns': [{'name': col[1], 'type': col[2]} for col in columns],
                'row_count': row_count
            })
        
        conn.close()
        return jsonify({'tables': tables_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables/<table_name>/schema', methods=['GET'])
def get_table_schema(table_name):
    """Get schema for a specific table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        conn.close()
        
        schema = [{'name': col[1], 'type': col[2]} for col in columns]
        return jsonify({'table': table_name, 'schema': schema})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example queries"""
    examples = [
        {
            'title': 'Count all employees (no privacy cost)',
            'query': 'SELECT COUNT(*) FROM employees',
            'description': 'Simple count query without privacy-sensitive data'
        },
        {
            'title': 'Top 5 companies by employee count',
            'query': 'SELECT Company_name, COUNT(*) FROM employees GROUP BY Company_name LIMIT 5',
            'description': 'Group by company and limit to top 5 results'
        },
        {
            'title': 'Average salary with DP (costs ε=1.0)',
            'query': 'SELECT AVG(PRIVATE Salary OF [1.0]) FROM employees',
            'description': 'Differentially private average of salaries'
        },
        {
            'title': 'Top 10 employees with highest budgets',
            'query': 'SELECT employee_id, SUM(PRIVATE budget OF [1.0]) FROM projects GROUP BY PUBLIC employee_id LIMIT 10',
            'description': 'Aggregate budget by employee with DP, limit to top 10'
        },
        {
            'title': 'Sample 20 company names',
            'query': 'SELECT Company_name FROM employees LIMIT 20',
            'description': 'Get a sample of 20 company names'
        },
        {
            'title': 'Max salary with custom epsilon',
            'query': 'SELECT MAX(PRIVATE Salary OF [0.5]) FROM employees',
            'description': 'Maximum salary with lower privacy budget'
        }
    ]
    return jsonify({'examples': examples})

if __name__ == '__main__':
    # Initialize rewriter before starting the app
    init_rewriter()
    print("=" * 70)
    print("🚀 DP System Backend Server")
    print("=" * 70)
    print("Server starting at: http://localhost:5000")
    print(f"Database: {DB_PATH}")
    print("API endpoints available:")
    print("  - POST /api/query                    - Execute DP query")
    print("  - GET  /api/budget/<user>            - Get budget status")
    print("  - POST /api/budget/<user>/reset      - Reset budget")
    print("  - GET  /api/budget/<user>/history    - Get budget history")
    print("  - GET  /api/tables                   - List tables with schemas")
    print("  - GET  /api/tables/<table>/schema    - Get table schema")
    print("  - GET  /api/examples                 - Get example queries")
    print("=" * 70)
    app.run(debug=True, port=5000)
