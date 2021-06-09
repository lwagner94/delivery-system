using DeliverySystemLib;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;

namespace GeoAPI.Controllers
{
    [Route("[controller]")]
    public class GeoController : Controller
    {
        private const string url = "https://nominatim.openstreetmap.org/search.php";
        private const string userAgent = "Delivery System / V1 Student Project for Smart Service Development TU Graz";

        [HttpGet("coordinates")]
        [Authorize]
        public async Task<ActionResult<Coordinates>> GetCoordinates([FromQuery] string address)
        {
            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Add("User-Agent", userAgent);
            var query = url + "?q=" + address.Replace(' ', '+') + "&format=jsonv2";
            var response = await httpClient.GetAsync(query);
            var data = await response.Content.ReadAsStringAsync();
            var geoData = await response.Content.ReadAsAsync<GeoData[]>();
            var result = geoData.Where(x => x.Osm_type == "node").OrderByDescending(x => x.Importance).FirstOrDefault();
            if (result == null)
            {
                return BadRequest();
            }
            return new Coordinates()
            {
                Latitude = result.Lat,
                Longitude = result.Lon
            };
        }

        [HttpPost("test_reset")]
        public IActionResult Reset()
        {
            try
            {
                var e = Environment.GetEnvironmentVariable("INTEGRATION_TEST");
                if (e == "1")
                {
                    return Ok();
                }
            }
            catch (Exception) { }

            return NotFound();
        }
    }
}
