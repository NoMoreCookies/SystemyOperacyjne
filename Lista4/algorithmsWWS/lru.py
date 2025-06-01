from collections import deque
import copy

def lru_wws_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                      delta_t=100, c_factor=0.6):
    current_time = 0
    total_frames = virtual_capacity

    # Początkowy podział ramek proporcjonalny
    process_frame_counts = [max(1, int(total_frames * p)) for p in process_proportions]
    process_frame_counts[0] += total_frames - sum(process_frame_counts)  # korekta zaokrągleń

    pamiec_procesow = {p: {} for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}
    access_history = {p: deque(maxlen=delta_t) for p in range(process_count)}
    suspended = {p: False for p in range(process_count)}
    saved_state = {p: {} for p in range(process_count)}  # snapshot stanu procesu przy zawieszeniu
    log_data = []

    c = max(1, int(c_factor * delta_t))

    for idx, (process_id, page, time, _) in enumerate(sorted(ciag_odwolan, key=lambda x: x[2])):

        if suspended[process_id]:
            continue

        access_history[process_id].append(page)
        pamiec = pamiec_procesow[process_id]
        frame_limit = max(1, process_frame_counts[process_id])

        # Aktualizacja wieku
        for s in pamiec:
            pamiec[s] += 1

        # Odwołanie do strony
        if page in pamiec:
            pamiec[page] = 0
        else:
            bledy_procesow[process_id] += 1
            if len(pamiec) < frame_limit:
                pamiec[page] = 0
            else:
                to_remove = max(pamiec.items(), key=lambda x: x[1])[0]
                del pamiec[to_remove]
                pamiec[page] = 0

        pamiec_procesow[process_id] = pamiec

        # --- Reorganizacja co C kroków ---
        if (idx + 1) % c == 0:
            current_time += c
            current_wss = {
                pid: len(set(access_history[pid])) if not suspended[pid] else 0
                for pid in range(process_count)
            }

            total_wss = sum(current_wss.values())

            # Wstrzymywanie procesów jeśli potrzebne
            while total_wss > total_frames:
                active = [pid for pid in range(process_count) if not suspended[pid]]
                if len(active) <= 1:  # zostaw chociaż 1 proces aktywny
                    break
                victim = max(active, key=lambda p: current_wss[p])
                suspended[victim] = True
                saved_state[victim] = copy.deepcopy(pamiec_procesow[victim])
                total_wss -= current_wss[victim]
                total_frames += process_frame_counts[victim]
                process_frame_counts[victim] = 0
                pamiec_procesow[victim].clear()

            # Przydział ramek według WSS
            active_processes = [pid for pid in range(process_count) if not suspended[pid]]
            if active_processes and total_wss > 0:
                total_assigned = 0
                for pid in active_processes:
                    proportion = current_wss[pid] / total_wss
                    allocated = max(1, round(proportion * total_frames))
                    process_frame_counts[pid] = allocated
                    total_assigned += allocated

                # Korekta nadmiaru/niedoboru
                diff = total_frames - total_assigned
                if diff != 0:
                    max_pid = max(active_processes, key=lambda p: current_wss[p])
                    process_frame_counts[max_pid] += diff

            # Wznawianie procesów
            for pid in range(process_count):
                if suspended[pid]:
                    required = len(set(access_history[pid]))
                    if required <= total_frames:
                        suspended[pid] = False
                        process_frame_counts[pid] = max(1, required)
                        total_frames -= process_frame_counts[pid]
                        pamiec_procesow[pid] = copy.deepcopy(saved_state[pid])

            # Log
            for pid in range(process_count):
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_wss': current_wss[pid],
                    'allocated_frames': process_frame_counts[pid],
                    'process_suspended': suspended[pid]
                })

    return bledy_procesow, suspended, log_data
