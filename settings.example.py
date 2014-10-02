# chininux settings

# URLs from which information is fetched
GIURLS = ["http://wiki.ninux.org/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziCalabria",
          "http://wiki.ninux.org/Firenze/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziMarche",
          "http://wiki.ninux.org/indirizzi-sicilia",
          "phpipam://chininux:1a4fa39d2635bcd1bbcf0341d5030b60@indirizzi.frm.ninux.org"
         ]

# chininux-server parameters
bindPort = 43
bindAddress = "::"
refreshInterval = 3600

# fixed header and footer that are printed at each query
headerstring = "% This is the chininux ninux.org Query Service.\n% The objects don't follow a specific format.\n"
footerstring = "\n% This query was served by the chininux ninux.org Query Service.\n"


