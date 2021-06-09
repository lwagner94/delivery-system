using Dapper.Contrib.Extensions;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace AgentAPI
{
    public class AgentState
    {
        public string Status { get; set; }
        public double Longitude { get; set; }
        public double Latitude { get; set; }
        public string Current_job { get; set; }
    }
}
