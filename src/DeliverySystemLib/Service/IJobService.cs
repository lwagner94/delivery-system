using Microsoft.AspNetCore.Http;
using System.Net.Http;
using System.Threading.Tasks;

namespace DeliverySystemLib
{
    public interface IJobService
    {
        Task<HttpResponseMessage> Get(string id, HttpRequest request);
    }
}