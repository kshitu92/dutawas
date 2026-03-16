CONSULATES = {
    'washington-state': {
        'url': 'https://nepalconsulate.org',  # Main website
        'file': 'consulates/united-states/washington-state.md',
        'selectors': {
            'address': {'pattern': r'(?:\d+[A-Za-z\s,]+(?:Suite|St|Ave|Way)[A-Za-z\s,]+)?(?:Redmond|Bellevue|Seattle)[A-Za-z\s,]+(?:WA|Washington)\s+\d{5}'},
            'phone': {'pattern': r'(?:Phone|Tel|Contact)?\s*:?\s*(?:\+1|1-)?\s*(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}'},
            # email is JS-obfuscated by Cloudflare on this site — cannot be scraped as plain text
            # hours are not present on the website
        }
    },
    # boston: no separate consulate exists; MA falls under New York jurisdiction (see consulates/united-states/boston.md)
    'new-york': {
        'url': 'https://nyc.nepalconsulate.gov.np/contact-us/',
        'file': 'consulates/united-states/new-york.md',
        'selectors': {
            'email': {'pattern': r'cgnnewyork@mofa\.gov\.np'},
            # address/phone/hours not rendered as plain text on the contact page
        }
    },
    'canberra': {
        'url': 'https://au.nepalembassy.gov.np/contact-us/',
        'file': 'consulates/australia/canberra.md',
        'selectors': {
            'address': {'pattern': r'Canberra,\s*Australia'},
            'email': {'pattern': r'(?:consular\.canberra|eoncanberra)@mofa\.gov\.np'},
            'hours': {'pattern': r'9am\s+to\s+1pm,?\s*2pm\s+to\s+5pm'}  # full hours appear as a single text node
        }
    },
    'sydney': {
        'url': 'https://consulatenepal.org/contact-us/',
        'file': 'consulates/australia/sydney.md',
        'selectors': {
            'address': {'pattern': r'Suite\s*2,\s*Level\s*5,\s*263\s+Clarence\s+Street,\s*Sydney,\s*NSW\s*2000(?:\s+Australia)?'},
            'phone': {'pattern': r'(?:\+?61|0)\s*\(?2\)?[\s-]?\d{4}[\s-]?\d{4}'},
            'email': {'pattern': r'info@consulatenepal\.org'},
            'hours': {'pattern': r'(?:Mon|Monday)\s*\W+\s*(?:Fri|Friday)\s*:\s*10(?::?00)?\s*am\s*\W+\s*3(?::?00)?\s*pm'}
        }
    },
    'western-australia': {
        'url': 'https://www.consulateofnepal.org.au/contact/',
        'file': 'consulates/australia/western-australia.md',
        'selectors': {
            'address': {'pattern': r'Perth\s*WA\s*6000'},  # address is split across separate text nodes; match zip line
            'phone': {'pattern': r'(?:\+?61|0)\s*408\s*030\s*477'},
            'email': {'pattern': r'info@consulateofnepal\.org\.au'},
            'hours': {'pattern': r'Monday\s+to\s+Friday\s+9[.:]00\s*AM\s+to\s+4[.:]00\s*PM'}  # matches the combined hours line on the page
        }
    },
    'south-australia': {
        'url': 'https://www.nepal-consulate.net.au/contact-us',
        'file': 'consulates/australia/south-australia.md',
        'selectors': {
            'address': {'pattern': r'325\s+H[ae]mpstead\s+R(?:d|oad).*(?:Northfield).*(?:SA|South\s+Australia)\s*5085'},
            'phone': {'pattern': r'(?:\+?61\s*43|043)\s*448\s*6000'},
            'email': {'pattern': r'adelaide@nepal-consulate\.net\.au'},
            'hours': {'pattern': r'(?:Office\s+Hours\s*:\s*)?By\s+appointment'}
        }
    },
    'victoria': {
        'url': 'https://nepalconsulatevictoria.com.au/contact-us/',
        'file': 'consulates/australia/victoria.md',
        'selectors': {
            'address': {'pattern': r'3A\s+Belair\s+Avenue.*Glenroy,?\s*VIC\s*3046'},
            'phone': {'pattern': r'(?:\(\+?61\s*3\)|\+?61\s*3|03)[\s-]?\d{4}[\s-]?\d{4}'},
            # email is JS-obfuscated by Cloudflare on this site — cannot be scraped as plain text
        }
    }
}
