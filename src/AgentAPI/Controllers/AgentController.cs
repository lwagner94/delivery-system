using Microsoft.AspNetCore.Mvc;
using System;
using System.Linq;
using System.Threading.Tasks;
using System.Data;
using Dapper.Contrib.Extensions;
using System.Net;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;
using DeliverySystemLib;

namespace AgentAPI
{
    [Route("[controller]")]
    public class AgentController : Controller
    {
        private readonly string[] validAgentStates = { "off_duty", "idle", "picking_up", "delivering" };

        private readonly IDataAccess dataAccess;
        private readonly IAuthService authService;
        private readonly IJobService jobService;

        public string UserId
        {
            get
            {
                return User.Claims.Where(c => c.Type == ClaimTypes.NameIdentifier).First().Value;
            }
        }

        public AgentController(IDataAccess dataAccess, IAuthService authService, IJobService jobService)
        {
            this.dataAccess = dataAccess;
            this.authService = authService;
            this.jobService = jobService;
        }

        [HttpGet("{id}")]
        [Authorize]
        public async Task<ActionResult<AgentState>> GetAgentState(string id)
        {
            if (id.ToLower() == "self")
            {
                id = UserId;
            }

            var authResponse = await authService.Get(id, Request);
            if (authResponse.StatusCode == HttpStatusCode.OK)
            {
                using var conn = dataAccess.GetConnection();
                if (!(conn.Get<AgentStateTable>(id) is AgentState entry))
                {
                    return NotFound("Agent has not yet reported a status.");
                }
                return Ok(entry);
            }
            else
            {
                return StatusCode((int)authResponse.StatusCode);
            }
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "agent")]
        public async Task<IActionResult> UpdateAgentState([FromBody] AgentState agentState, string id)
        {
            if (id.ToLower() == "self" || UserId == id || id == null)
            {
                if (!string.IsNullOrEmpty(agentState.Current_job))
                {
                    var jobResponse = await jobService.Get(agentState.Current_job, Request);
                    if (!jobResponse.IsSuccessStatusCode)
                    {
                        return BadRequest("Invalid job id.");
                    }
                }
                agentState.Status = agentState.Status.ToLower();
                if (!validAgentStates.Contains(agentState.Status))
                {
                    return BadRequest("Invalid agent status.");
                }
                if (agentState.Latitude < -90 || agentState.Latitude > 90)
                {
                    return BadRequest("The valid range of latitude is -90 and 90.");
                }
                if (agentState.Longitude < -180 || agentState.Longitude > 180)
                {
                    return BadRequest("The valid range of longitude is -180 and 180.");
                }

                using var conn = dataAccess.GetConnection();
                var dbEntry = new AgentStateTable(agentState)
                {
                    Id = UserId
                };
                if (!conn.Update(dbEntry))
                {
                    conn.Insert(dbEntry);
                }

                return Ok();
            }
            else
            {
                return StatusCode(403, "You may only update your own agent status.");
            }
        }

        [HttpPost("test_reset")]
        public IActionResult Reset()
        {
            try
            {
                var e = Environment.GetEnvironmentVariable("INTEGRATION_TEST");
                if (e == "1")
                {
                    using var conn = dataAccess.GetConnection();
                    var dbEntries = conn.GetAll<AgentStateTable>();
                    foreach (var entry in dbEntries)
                    {
                        conn.Delete(entry);
                    }
                    return Ok();
                }                
            }
            catch (Exception) { }

            return NotFound();
        }
    }
}
