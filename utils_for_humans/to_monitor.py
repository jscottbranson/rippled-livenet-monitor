'''
A list of validators for use in testing the bot.
This list can be imported into dict_convert.py for easily generating a set of
servers to monitor.
'''
SERVERS = [
    {"url": "wss://xrplcluster.com:443", "server_name": "Cluster", "ssl_verify": True,},
]

VALIDATORS = [
    {"master_key": "nHUcNC5ni7XjVYfCMe38Rm3KQaq27jw7wJpcUYdo4miWwpNePRTw", "server_name": "Cabbit.Tech",},
    {"master_key": "nHUFE9prPXPrHcG3SkwP1UzAQbSphqyQkQK9ATXLZsfkezhhda3p", "server_name": "Alloy",},
    {"master_key": "nHB8QMKGt9VB4Vg71VszjBVQnDW3v3QudM4DwFaJfy96bj4Pv9fA", "server_name": "Bithomp",},
    {"master_key": "nHUd8g4DWm6HgjGTjKKSfYiRyf8qCvEN1PXR7YDJ5QTFyAnZHkbW", "server_name": "Brex",},
    {"master_key": "nHUwGQrfZfieeLFeGRdGnAmGpHBCZq9wvm5c59wTc2JhJMjoXmd8", "server_name": "XRPGoat",},
    {"master_key": "nHBWa56Vr7csoFcCnEPzCCKVvnDQw3L28mATgHYQMGtbEfUjuYyB", "server_name": "Vet",},
    {"master_key": "nHUge3GFusbqmfYAJjxfKgm2j4JXGxrRsfYMcEViHrFSzQDdk5Hq", "server_name": "Katczynski",},
    {"master_key": "nHUvzia57LRXr9zqnYpyFUFeKvis2tqn4DkXBVGSppt5M4nNq43C", "server_name": "Digifin",},
    {"master_key": "nHUnhRJK3csknycNK5SXRFi8jvDp3sKoWvS9wKWLq1ATBBGgPBjp", "server_name": "PeerIsland",},
    {"master_key": "nHU4bLE3EmSqNwfL4AP1UZeTNPrSPPP6FXLKXo2uqfHuvBQxDVKd", "server_name": "Ripple.com",},
    {"master_key": "nHUtmbn4ALrdU6U8pmd8AMt4qKTdZTbYJ3u1LHyAzXga3Zuopv5Y", "server_name": "Towo",},
    {"master_key": "nHUryiyDqEtyWVtFG24AAhaYjMf9FRLietbGzviF3piJsMm9qyDR", "server_name": "Bitrue",},
    {"master_key": "nHUbgDd63HiuP68VRWazKwZRzS61N37K3NbfQaZLhSQ24LGGmjtn", "server_name": "ANU.edu.au",},
    {"master_key": "nHUpDEZX5Zy9auiu4yhDmhirNu6PyB1LvzQEL9Mxmqjr818w663q", "server_name": "XSpectar",},
    {"master_key": "nHUED59jjpQ5QbNhesXMhqii9gA8UfbBmv3i5StgyxG98qjsT4yn", "server_name": "Arrington",},
    {"master_key": "nHDB2PAPYqF86j9j3c6w1F1ZqwvQfiWcFShZ9Pokg9q4ohNDSkAz", "server_name": "XRPScan",},
    {"master_key": "nHUvcCcmoH1FJMMC6NtF9KKA4LpCWhjsxk2reCQidsp5AHQ7QY9H", "server_name": "Jon Nilsen",},
    {"master_key": "nHUY14bKLLm72ukzo2t6AVnQiu4bCd1jkimwWyJk3txvLeGhvro5", "server_name": "Gatehub",},
    {"master_key": "nHUfPizyJyhAJZzeq3duRVrZmsTZfcLn7yLF5s2adzHdcHMb9HmQ", "server_name": "UNIC.ac.cy",},
    {"master_key": "nHUXeusfwk61c4xJPneb9Lgy7Ga6DVaVLEyB29ftUdt9k2KxD6Hw", "server_name": "XRPL-Labs",},
    {"master_key": "nHUq9tJvSyoXQKhRytuWeydpPjvTz3M9GfUpEqfsg9xsewM7KkkK", "server_name": "UCL.ac.uk",},
    {"master_key": "nHU2k8Po4dgygiQUG8wAADMk9RqkrActeKwsaC9MdtJ9KBvcpVji", "server_name": "Eminence",},
    {"master_key": "nHUdjQgg33FRu88GQDtzLWRw95xKnBurUZcqPpe3qC9XVeBNrHeJ", "server_name": "Robert Swarthout",},
    {"master_key": "nHUFCyRCrUjvtZmKiLeF8ReopzKuUoKeDeXo3wEUBVSaawzcSBpW", "server_name": "UNC.edu",},
    {"master_key": "nHBidG3pZK11zQD6kpNDoAhDxH6WLGui6ZxSbUx7LSqLHsgzMPec", "server_name": "Bitso",},
    {"master_key": "nHUpDPFoCNysckDSHiUBEdDXRu2iYLUgYjTzrj3bde5iDRkNtY8f", "server_name": "USP.br",},
    {"master_key": "nHDH7bQJpVfDhVSqdui3Z8GPvKEBQpo6AKHcnXe21zoD4nABA6xj", "server_name": "Waterloo",},
    {"master_key": "nHUVPzAmAmQ2QSc4oE1iLfsGi17qN2ado8PhxvgEkou76FLxAz7C", "server_name": "KU.edu",},
    {"master_key": "nHULqGBkJtWeNFjhTzYeAsHA3qKKS7HoBh8CV3BAGTGMZuepEhWC", "server_name": "Berkeley.edu",},
    {"master_key": "nHBdXSF6YHAHSZUk7rvox6jwbvvyqBnsWGcewBtq8x1XuH6KXKXr", "server_name": "FTSO.eu",},
    {"master_key": "nHU95JxeaHJoSdpE7R49Mxp4611Yk5yL9SGEc12UDJLr4oEUN4NT", "server_name": "Flagship Solutions",},
    {"master_key": "nHUpcmNsxAw47yt2ADDoNoQrzLyTJPgnyq16u6Qx2kRPA17oUNHz", "server_name": "ISRDC.in",},
    {"master_key": "nHUpJSKQTZdB1TDkbCREMuf8vEqFkk84BcvZDhsQsDufFDQVajam", "server_name": "Data443",},
    {"master_key": "nHBgiH2aih5JoaL3wbiiqSQfhrC21vJjxXoCoD2fuqcNbriXsfLm", "server_name": "AtTokyo",},
    {"master_key": "nHU3AenyRuJ4Yei4YHkh6frZg8y2RwXznkMAomUE1ptV5Spvqsih", "server_name": "aesthetes.art",},
]
