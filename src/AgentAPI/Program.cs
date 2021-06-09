using AgentAPI;
using Dapper;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using System.Linq;
using System.Threading.Tasks;

namespace AgentAPI
{
    public class Program
    {
        public static string dbPath = "/tmp/data/agent_state.db";

        public static void Main(string[] args)
        {
            CreateDB();
            CreateHostBuilder(args).Build().Run();
        }

        public static void CreateDB()
        {
            SQLiteConnection.CreateFile(dbPath);
            string sql = "CREATE TABLE IF NOT EXISTS AgentStates (Id TEXT PRIMARY KEY, Current_job TEXT, Longitude REAL, Latitude REAL, Status TEXT)";
            using var conn = new SqliteDataAccess().GetConnection();
            conn.Execute(sql);
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                });
    }
}
