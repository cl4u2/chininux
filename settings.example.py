# chininux settings

# URLs from which information is fetched
GIURLS = ["http://wiki.ninux.org/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziCalabria",
          "http://wiki.ninux.org/Firenze/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziMarche",
          "http://wiki.ninux.org/indirizzi-sicilia",
          "http://wiki.ninux.org/IndirizziVerona",
          "http://wiki.ninux.org/Lombardia/GestioneIndirizzi",
          "http://wiki.ninux.org/indirizzi-sicilia",
          "http://wiki.ninux.org/IndirizziCampania",
          "phpipam://chininux:1a4fa39d2635bcd1bbcf0341d5030b60@ipam.ninux.org",
          "nodeshot://ninux.nodeshot.org"
         ]

# chininux-server parameters
bindPort = 43
bindAddress = "::"
refreshInterval = 3600

# fixed header and footer that are printed at each query
headerstring = "% This is the chininux ninux.org Query Service.\n% The objects don't follow a specific format.\n"
footerstring = "\n% This query was served by the chininux ninux.org Query Service.\n"


