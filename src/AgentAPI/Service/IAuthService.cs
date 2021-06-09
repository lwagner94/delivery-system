using Microsoft.AspNetCore.Http;
using System.Net.Http;
using System.Threading.Tasks;

namespace AgentAPI
{
    public interface IAuthService
    {
        Task<HttpResponseMessage> Get(string id, HttpRequest request);

        HttpClient GetAuthorizedClient(HttpRequest request);
    }
}