# chininux settings

# URLs from which information is fetched
GIURLS = ["http://wiki.ninux.org/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziCalabria",
          "http://wiki.ninux.org/Firenze/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziMarche",
          "http://wiki.ninux.org/indirizzi-sicilia"
         ]

# chininux-server parameters
bindPort = 43
bindAddress = "0.0.0.0"
refreshInterval = 3600

# fixed header and footer that are printed at each query
headerstring = "% This is the chinux ninux.org Query Service.\n% The objects don't follow a specific format.\n"
footerstring = "\n% This query was served by the chininux ninux.org Query Service.\n"

