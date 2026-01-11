# DP System - Differential Privacy Query System

A fullstack application for executing SQL queries with differential privacy guarantees on sensitive databases.

## Features

- **Differential Privacy**: Automatic noise injection for PRIVATE aggregations using Laplace mechanism
- **Privacy Budget Management**: Track and enforce ε-differential privacy budget per user
- **SQL Support**: Extended SQL with PRIVATE/PUBLIC labels, supports SELECT, WHERE, GROUP BY, JOIN, LIMIT
- **HIPAA Compliance**: Blocks direct access to 35+ PII columns
- **Web Interface**: React frontend with real-time query execution and budget tracking

## Tech Stack

- **Backend**: Python 3.12, Flask, SQLite, ANTLR 4.13.1
- **Frontend**: React 18.2, Axios
- **Privacy**: (ε,0)-differential privacy with Laplace noise

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 16+
- Java 11+ (for ANTLR grammar regeneration)

1. **Install Python dependencies**:
   ```cmd
   cd backend
   pip install -r requirements.txt
   ```

2. **Initialize the database**:
   ```cmd
   python init_database.py
   ```
   This will create `database.db` and load data from CSV files.

3. **Start the backend server**:
   ```cmd
   python app.py
   ```
   The API will run on `http://localhost:5000`

### Frontend Setup

1. **Install Node dependencies**:
   ```cmd
   cd frontend
   npm install

### Setup

1. **Install Python dependencies**:
```bash
pip install flask flask-cors pandas numpy antlr4-python3-runtime
```

2. **Install frontend dependencies**:
```bash
cd frontend
npm install
```

3. **Initialize database** (if needed):
```bash
cd backend
python init_database.py
```

### Run

1. **Start backend**:
```bash
cd backend
python app.py
```
Backend runs on http://localhost:5000

2. **Start frontend** (in new terminal):
```bash
cd frontend
npm start
```
Frontend runs on http://localhost:3000

## Usage

### Query Syntax

**Basic queries**:
```sql
SELECT COUNT(*) FROM employees
SELECT Company_name FROM employees LIMIT 10
```

**Differential Privacy**:
```sql
SELECT AVG(PRIVATE Salary OF [1.0]) FROM employees
SELECT SUM(PRIVATE budget OF [0.5]) FROM projects GROUP BY PUBLIC employee_id LIMIT 5
```

**Syntax**:
- `PRIVATE column OF [epsilon]` - Apply DP with privacy cost ε
- `PUBLIC column` - No privacy cost for grouping
- `LIMIT n` - Restrict results to top n rows

## Database Schema

**employees** (100,000 rows):
- id, First_name, Last_name, Company_name, Address, City, County, State, ZIP, Phone1, Phone2, Email, Web, Salary (PRIVATE)

**projects** (50,000 rows):
- id, employee_id, project_name, budget (PRIVATE), deadline

## Privacy Budget

- Default: ε = 10.0 per user session
- Each PRIVATE aggregation consumes ε as specified
- Budget resets per user via UI or API

## API Endpoints

- `POST /api/query` - Execute DP query
- `GET /api/budget/:user` - Get budget status
- `POST /api/budget/:user/reset` - Reset budget
- `GET /api/tables` - List tables with schemas
- `GET /api/examples` - Get example queries

## Grammar

The DPDSL grammar is defined in `DPDSL.g4`. To regenerate parser:

```bash
java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor DPDSL.g4
```

## Project Structure

```
DP_System/
├── backend/
│   ├── app.py              # Flask API server
│   ├── init_database.py    # Database setup
│   └── database.db         # SQLite database
├── frontend/
│   └── src/
│       ├── App.js          # React main component
│       └── App.css         # UI styles
├── dp.py                   # DP rewriter core logic
├── DPDSL.g4               # ANTLR grammar definition
├── DPDSLParser.py         # Generated parser
└── start.bat              # Windows startup script
```

## License

MIT
1. Execute: `SELECT COUNT(*) FROM employees` (no cost)
2. Execute: `SELECT AVG(PRIVATE Salary OF [1.0]) FROM employees` (costs ε=1.0)
3. Check budget: Should show 9.0 remaining
4. Try a prohibited query: `SELECT Email FROM employees` (blocked by HIPAA)

## 📝 Troubleshooting

### Backend Issues
- **Import errors**: Make sure ANTLR files are generated in the root directory
- **Database not found**: Run `init_database.py` first
- **Port 5000 in use**: Change port in `app.py`

### Frontend Issues
- **Cannot connect to API**: Ensure backend is running on port 5000
- **CORS errors**: Check that flask-cors is installed
- **Port 3000 in use**: React will prompt to use another port

## 📚 Additional Information

### Configuration
Edit `DPDSLConfig` in `dp.py` to customize:
- Sensitivity bounds per column
- Privacy budget limits
- HIPAA column restrictions
- Audit logging settings

### Audit Logs
All queries are logged to `dpdsl_audit.jsonl` with:
- Timestamp and user ID
- Query hash
- Privacy cost
- Success/failure status

## 🔄 Development

### Regenerating Parser (if grammar changes)
```cmd
java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 -visitor DPDSL.g4
```

### Adding New Tables
1. Place CSV file in `root/databases/`
2. Run `init_database.py` to reload
3. Update sensitivity bounds in `DPDSLConfig` if needed

## 📄 License

This is an educational/research system demonstrating differential privacy concepts.

## 👥 Support

For issues or questions about the system, refer to the documentation in `dp.py` or check the example queries in the UI.

---

**Built with**: Flask, React, ANTLR, SQLite, Pandas, NumPy
