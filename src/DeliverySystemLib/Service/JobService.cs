using Microsoft.AspNetCore.Http;
using System.Net.Http;
using System.Threading.Tasks;

namespace DeliverySystemLib
{
    public class JobService : IJobService
    {
        private readonly string baseUri ="http://TODO/job/";
        private readonly IAuthService authService;

        public JobService(IAuthService authService)
        {
            this.authService = authService;
        }

        public async Task<HttpResponseMessage> Get(string id, HttpRequest request)
        {
            using var client = authService.GetAuthorizedClient(request);
            return await client.GetAsync(baseUri + id);
        }
    }
}
