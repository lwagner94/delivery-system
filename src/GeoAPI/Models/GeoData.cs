using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace GeoAPI
{
    public class GeoData
    {
        public long Place_id { get; set; }
        public string Licence { get; set; }
        public string Osm_type { get; set; }
        public long Osm_id { get; set; }
        public double[] Boundingbox { get; set; }
        public double Lat { get; set; }
        public double Lon { get; set; }
        public string Display_name { get; set; }
        public int Place_rank { get; set; }
        public string Category { get; set; }
        public string Type { get; set; }
        public double Importance { get; set; }
        public string Icon { get; set; }
    }
}
