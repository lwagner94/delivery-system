using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.Linq;
using System.Threading.Tasks;

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
