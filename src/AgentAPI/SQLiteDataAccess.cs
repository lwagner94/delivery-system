using System.Data;
using System.Data.SQLite;

namespace AgentAPI
{
    public class SqliteDataAccess : IDataAccess
    {
        public IDbConnection GetConnection()
        {
            return new SQLiteConnection($"Data Source={ Program.dbPath };Version=3;");
        }
    }
}
