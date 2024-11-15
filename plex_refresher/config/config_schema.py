CONFIG_SCHEMA = {
    'plex': {
        'required': True,
        'type': dict,
        'fields': {
            'url': {'type': str, 'required': True},
            'token': {'type': str, 'required': True},
            'libraries': {'type': (list, type(None)), 'required': False}
        }
    },
    'search': {  # New section
        'required': True,
        'type': dict,
        'fields': {
            'patterns': {'type': list, 'required': True},
            'case_sensitive': {'type': bool, 'required': False, 'default': False}
        }
    },
    'refresh': {
        'required': True,
        'type': dict,
        'fields': {
            'interval_seconds': {'type': int, 'required': True, 'min': 60},
            'delay_between_items': {'type': int, 'required': True, 'min': 1, 'max': 30},
            'dry_run': {'type': bool, 'required': False, 'default': True}
        }
    },
    'logging': {
        'required': True,
        'type': dict,
        'fields': {
            'level': {'type': str, 'required': True, 'values': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']},
            'format': {'type': str, 'required': True},
            'file': {'type': str, 'required': True},
            'max_size_mb': {'type': int, 'required': True, 'min': 1},
            'backup_count': {'type': int, 'required': True, 'min': 0}
        }
    }
}