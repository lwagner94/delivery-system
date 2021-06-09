using Dapper.Contrib.Extensions;

namespace DeliverySystemLib
{
    [Table("AgentStates")]
    public class AgentStateTable : AgentState
    {
        [ExplicitKey]
        public string Id { get; set; }

        public AgentStateTable()
        {

        }

        public AgentStateTable(AgentState agentState)
        {
            Current_job = agentState.Current_job;
            Longitude = agentState.Longitude;
            Latitude = agentState.Latitude;
            Status = agentState.Status; 
        }
    }
}
