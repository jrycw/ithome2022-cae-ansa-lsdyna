from schemas import TaskStatus

solver_type_mapping = {'smp': 'smp', 'mpp': 'mpp', 'hybrid': 'hyb'}
solver_precision_mapping = {'single': 's', 'double': 'd'}
solver_version_pool = ('12.0', '8.0', '8.1', '9.0', '9.1', '9.2', '10.0',
                       '10.1', '11.0', '11.1', '11.2', '12.0', '12.1', '13.0', 'Daily')
emogi_keys = [t.name for t in TaskStatus]
emogi_values = [e.encode('utf-8') for e in ('🟠', '🟢', '❌', '✅')]
emogi_mapping = dict(zip(emogi_keys, emogi_values))
