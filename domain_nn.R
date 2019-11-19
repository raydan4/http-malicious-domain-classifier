domainvals <- parse_double(sapply(malwaredomains, function(x) try(entropy(x))))
domainvals <- domainvals[!is.na(domainvals)]
