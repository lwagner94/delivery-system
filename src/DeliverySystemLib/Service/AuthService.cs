using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System.Net.Http;
using System.Security.Claims;
using System.Text.Encodings.Web;
using System.Threading.Tasks;

namespace DeliverySystemLib
{
    public class CustomTokenAuthOptions : AuthenticationSchemeOptions
    {
        public const string Name = "CustomTokenAuthentication";
        public string TokenHeaderName { get; set; } = "Authorization";
        public string TokenTypeName { get; set; } = "Bearer";
    }

    public class AuthService : AuthenticationHandler<CustomTokenAuthOptions>, IAuthService
    {
        private readonly string baseUri = "http://auth:5000/auth";
        private readonly IOptionsMonitor<CustomTokenAuthOptions> options;

        public AuthService(IOptionsMonitor<CustomTokenAuthOptions> options, ILoggerFactory logger, UrlEncoder encoder, ISystemClock clock)
            : base(options, logger, encoder, clock)
        {
            this.options = options;
        }

        public async Task<HttpResponseMessage> Get(string id, HttpRequest request)
        {
            using var client = GetAuthorizedClient(request);
            return await client.GetAsync(baseUri + "/user/" + id);
        }


        public HttpClient GetAuthorizedClient(HttpRequest request)
        {
            var client = new HttpClient();
            client.DefaultRequestHeaders.Add(options.CurrentValue.TokenHeaderName, options.CurrentValue.TokenTypeName + " " + 
                GetToken(request, options.CurrentValue));
            return client;
        }

        private static string GetToken(HttpRequest request, CustomTokenAuthOptions options)
        {
            if (request.Headers.ContainsKey(options.TokenHeaderName))
            {
                foreach (var authHeader in request.Headers[options.TokenHeaderName])
                {
                    if (authHeader.StartsWith(options.TokenTypeName))
                    {
                        return authHeader.Substring(options.TokenTypeName.Length + 1).Trim();
                    }
                }
            }            
            return null;
        }

        protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
        {
            if (GetToken(Request, Options) == null)
            {
                return AuthenticateResult.Fail($"Missing {Options.TokenHeaderName} Token.");
            }

            HttpResponseMessage authResponse;
            try
            {
                authResponse = await Get("self", Request);
            }
            catch (System.Exception ex)
            {
                return AuthenticateResult.Fail($"Auth service failed { ex.GetType().ToString() }.");
            }

            if (authResponse.IsSuccessStatusCode)
            {
                var userInfo = await authResponse.Content.ReadAsAsync<UserInfo>();
                var claims = new[] {
                    new Claim(ClaimTypes.NameIdentifier, userInfo.Id),
                    new Claim(ClaimTypes.Email, userInfo.Email),
                    new Claim(ClaimTypes.Role, userInfo.Role) };
                var principal = new ClaimsPrincipal(new ClaimsIdentity(claims, Scheme.Name));
                var ticket = new AuthenticationTicket(principal, Scheme.Name);
                return AuthenticateResult.Success(ticket);
            }
            return AuthenticateResult.Fail($"Auth service responded with status code { authResponse.StatusCode }.");
        }
    }
}
