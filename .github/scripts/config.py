CONSULATES = {
    'washington-state': {
        'url': 'https://nepalconsulate.org',
        'file': 'consulates/washington-state.md',
        'selectors': {
            'address': {'pattern': r'Bellevue|Redmond'},
            'phone': {'pattern': r'\+1.*\d{3}.*\d{4}'},
            'email': {'pattern': r'[\w\.-]+@[\w\.-]+'},
            'hours': {'pattern': r'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday'}
        }
    },
    'boston': {
        'url': 'https://bostonconsulatenepal.org',
        'file': 'consulates/boston.md',
        'selectors': {
            'address': {'pattern': r'Boston|Massachusetts'},
            'phone': {'pattern': r'\+1.*\d{3}.*\d{4}'},
            'email': {'pattern': r'[\w\.-]+@[\w\.-]+'},
            'hours': {'pattern': r'Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday'}
        }
    }
}
