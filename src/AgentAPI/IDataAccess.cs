using System.Data;

namespace AgentAPI
{
    public interface IDataAccess
    {
        IDbConnection GetConnection();
    }
}