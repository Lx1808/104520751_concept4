import json
import psutil
import os
import subprocess
from collections import defaultdict
from typing import List
from .model import MalwareDetectionModel
from ..file_upload.utils import update_scan_result


def safe_process_iter():
    for proc in psutil.process_iter(['pid', 'ppid', 'name', 'num_threads']):
        try:
            yield proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def safe_open_files(proc):
    try:
        return proc.open_files()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        return []

def safe_connections(proc):
    try:
        return proc.connections()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        return []

def safe_memory_maps(proc):
    try:
        return proc.memory_info()
    except (psutil.AccessDenied, psutil.ZombieProcess):
        return None

def get_system_services():
    try:
        # 计算 /proc 目录中的进程数量
        return len([d for d in os.listdir('/proc') if d.isdigit()])
    except Exception:
        return 0

def extract_features(file_path: str) -> List[float]:
    features = {}

    # Extract all 52 features
    processes = list(safe_process_iter())
    features['pslist.nproc'] = len(processes)
    features['pslist.nppid'] = len(set(p.info['ppid'] for p in processes if p.info['ppid'] is not None))
    thread_counts = [p.info['num_threads'] for p in processes if p.info['num_threads'] is not None]
    features['pslist.avg_threads'] = sum(thread_counts) / len(thread_counts) if thread_counts else 0

    total_open_files = sum(len(safe_open_files(p)) for p in processes)
    features['pslist.avg_handlers'] = total_open_files / len(processes) if processes else 0

    total_dlls = sum(1 for p in processes for m in safe_memory_maps(p) or [] if m)
    features['dlllist.ndlls'] = total_dlls
    features['dlllist.avg_dlls_per_proc'] = total_dlls / len(processes) if processes else 0

    handle_types = defaultdict(int)
    for proc in processes:
        for conn in safe_connections(proc):
            handle_types[conn.type] += 1

    features['handles.nhandles'] = sum(handle_types.values())
    features['handles.avg_handles_per_proc'] = features['handles.nhandles'] / len(processes) if processes else 0
    features['handles.nfile'] = handle_types.get('file', 0)
    features['handles.nevent'] = handle_types.get('event', 0)
    features['handles.ndesktop'] = 0  # Not available on Linux
    features['handles.nkey'] = handle_types.get('key', 0)
    features['handles.nthread'] = handle_types.get('thread', 0)
    features['handles.ndirectory'] = handle_types.get('directory', 0)
    features['handles.nsemaphore'] = handle_types.get('semaphore', 0)
    features['handles.ntimer'] = handle_types.get('timer', 0)
    features['handles.nsection'] = handle_types.get('section', 0)
    features['handles.nmutant'] = handle_types.get('mutant', 0)

    # ldrmodules, malfind, psxview related features (placeholder values)
    for prefix in ['ldrmodules', 'malfind', 'psxview']:
        for suffix in ['not_in_load', 'not_in_init', 'not_in_mem', 'ninjections', 'commitCharge', 'protection',
                       'uniqueInjections', 'not_in_pslist', 'not_in_eprocess_pool', 'not_in_ethread_pool',
                       'not_in_pspcid_list', 'not_in_csrss_handles', 'not_in_session', 'not_in_deskthrd']:
            features[f'{prefix}.{suffix}'] = 0
        for suffix in ['not_in_load_avg', 'not_in_init_avg', 'not_in_mem_avg', 'not_in_pslist_false_avg',
                       'not_in_eprocess_pool_false_avg', 'not_in_ethread_pool_false_avg',
                       'not_in_pspcid_list_false_avg', 'not_in_csrss_handles_false_avg', 'not_in_session_false_avg',
                       'not_in_deskthrd_false_avg']:
            features[f'{prefix}.{suffix}'] = 0

    features['modules.nmodules'] = len(psutil.disk_partitions())

    features['svcscan.nservices'] = get_system_services()
    features['svcscan.nactive'] = features['svcscan.nservices']  # Assuming all services are active
    features['svcscan.kernel_drivers'] = 0  # Not easily accessible on Linux
    features['svcscan.fs_drivers'] = 0  # Not easily accessible on Linux
    features['svcscan.process_services'] = features['svcscan.nservices']
    features['svcscan.shared_process_services'] = 0  # Not applicable on Linux

    features['callbacks.ncallbacks'] = 0
    features['callbacks.nanonymous'] = 0
    features['callbacks.ngeneric'] = 0

    # Load selected features
    current_dir = os.path.dirname(os.path.abspath(__file__))
    feature_path = os.path.join(current_dir, 'content', 'saved_model_4class')
    with open(os.path.join(feature_path, 'selected_features.json'), 'r') as f:
        selected_features = json.load(f)

    # Only return selected features
    return [features[feature] for feature in selected_features]

async def scan_file(file_path: str, file_id: str) -> None:
    try:
        features = extract_features(file_path)
        model = MalwareDetectionModel()
        scan_result = model.predict(features)

        # Update the scan result in the database
        update_scan_result(file_id, scan_result)
    except FileNotFoundError as e:
        error_message = f"File not found: {str(e)}"
        print(error_message)
        update_scan_result(file_id, {"error": error_message, "status": "failed"})
    except PermissionError as e:
        error_message = f"Permission denied: {str(e)}"
        print(error_message)
        update_scan_result(file_id, {"error": error_message, "status": "failed"})
    except Exception as e:
        error_message = f"Unexpected error during file scan: {str(e)}"
        print(error_message)
        update_scan_result(file_id, {"error": error_message, "status": "failed"})