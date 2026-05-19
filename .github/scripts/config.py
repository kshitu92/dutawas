CONSULATES = {
    'washington-state': {
        'url': 'https://nepalconsulate.org',  # Main website
        'file': 'consulates/united-states/washington-state.md',
        'selectors': {
            'address': {'pattern': r'(?:\d+[A-Za-z\s,]+(?:Suite|St|Ave|Way)[A-Za-z\s,]+)?(?:Redmond|Bellevue|Seattle)[A-Za-z\s,]+(?:WA|Washington)\s+\d{5}'},
            'phone': {'pattern': r'(?:Phone|Tel|Contact)?\s*:?\s*(?:\+1|1-)?\s*(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}'},
            'email': {'pattern': r'(?:Email|E-mail)?\s*:?\s*[\w\.-]+@(?:nepalconsulatewa\.(?:us|org)|mofa\.gov\.np)'},
            'hours': {'pattern': r'(?:Hours?|Office\s+Hours?|Business\s+Hours?)\s*:?\s*(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)[^<>{}\[\]]*?(?:AM|PM|am|pm)'}
        }
    },
    'boston': {
        'url': 'https://www.nepalembassy.org/cgboston',  # Updated URL
        'file': 'consulates/united-states/boston.md',
        'selectors': {
            'address': {'pattern': r'(?:Boston|Massachusetts).*\d{5}'},
            'phone': {'pattern': r'(?:\+1|1-)?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'},
            'email': {'pattern': r'[\w\.-]+@(?:cgboston\.gov\.np|mofa\.gov\.np)'},
            'hours': {'pattern': r'(?i)(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday).*(?:am|pm)'}
        }
    },
    'new-york': {
        'url': 'https://nyc.nepalconsulate.gov.np',
        'file': 'consulates/united-states/new-york.md',
        'selectors': {
            'address': {'pattern': r'(?:New\s*York|NY).*\d{5}'},
            'phone': {'pattern': r'(?:\+1|1-)?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'},
            'email': {'pattern': r'[\w\.-]+@(?:nepalconsulate\.org|mofa\.gov\.np)'},
            'hours': {'pattern': r'(?i)(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday).*(?:am|pm)'}
        }
    },
    'dallas': {
        'url': 'https://dls.nepalconsulate.gov.np',
        'file': 'consulates/united-states/dallas.md',
        'selectors': {
            'address': {'pattern': r'(?:Dallas|Texas|TX).*\d{5}'},
            'phone': {'pattern': r'(?:\+1|1-)?\s*\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'},
            'email': {'pattern': r'[\w\.-]+@nepalconsulatedallas\.org'},
            'hours': {'pattern': r'(?i)(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday).*(?:am|pm)'}
        }
    }
}
