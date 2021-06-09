#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

FROM mcr.microsoft.com/dotnet/aspnet:3.1 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:3.1 AS build
WORKDIR /src
COPY ["GeoAPI/GeoAPI.csproj", "GeoAPI/"]
RUN dotnet restore "GeoAPI/GeoAPI.csproj"
COPY . .
WORKDIR "/src/GeoAPI"
RUN dotnet build "GeoAPI.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "GeoAPI.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "GeoAPI.dll"]