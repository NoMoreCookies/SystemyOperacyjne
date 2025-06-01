import random
from collections import deque

def rand_wws_procesowy(ciag_odwolan, virtual_capacity, process_count, process_proportions,
                      delta_t=10, c_factor=0.3):

    # Początkowy przydział ramek
    process_frame_counts = [int(virtual_capacity * p) for p in process_proportions]
    process_frame_counts[0] += virtual_capacity - sum(process_frame_counts)

    # Inicjalizacja pamięci i buforów
    pamiec_procesow = {p: set() for p in range(process_count)}
    bledy_procesow = {p: 0 for p in range(process_count)}
    recent_pages = {p: deque(maxlen=delta_t) for p in range(process_count)}
    suspended = {p: False for p in range(process_count)}
    available_frames = 0

    total_requests_sorted = sorted(ciag_odwolan, key=lambda x: x[2])

    log_data = []
    current_time = 0

    c = int(c_factor * delta_t)
    if c == 0:
        c = 1  # minimum co 1 odwołanie

    for idx, (process_id, page, time, _) in enumerate(total_requests_sorted):

        if suspended[process_id]:
            recent_pages[process_id].append(None)
        else:
            pamiec = pamiec_procesow[process_id]
            ramki = process_frame_counts[process_id]

            if page not in pamiec:
                bledy_procesow[process_id] += 1
                if len(pamiec) < ramki:
                    pamiec.add(page)
                else:
                    if pamiec:
                        usuwana = random.choice(list(pamiec))
                        pamiec.remove(usuwana)
                    pamiec.add(page)

            recent_pages[process_id].append(page)
            pamiec_procesow[process_id] = pamiec

        # Aktualizacja co c odwołań
        if (idx + 1) % c == 0:
            available_frames = virtual_capacity - sum(
                process_frame_counts[pid] for pid in range(process_count) if not suspended[pid]
            )

            # Oblicz WSS dla wszystkich procesów
            wws_sizes = {}
            for pid in range(process_count):
                okno = [p for p in recent_pages[pid] if p is not None]
                wws_sizes[pid] = len(set(okno))

            for pid in range(process_count):
                frame_action = None
                wws_size = wws_sizes[pid]

                if wws_size > process_frame_counts[pid] and available_frames < (wws_size - process_frame_counts[pid]):
                    if not suspended[pid]:
                        suspended[pid] = True
                        available_frames += process_frame_counts[pid]
                        process_frame_counts[pid] = 0
                        pamiec_procesow[pid].clear()
                        recent_pages[pid].clear()
                        frame_action = "suspended"
                else:
                    if not suspended[pid]:
                        current_frames = process_frame_counts[pid]
                        diff = wws_size - current_frames
                        if diff > 0 and available_frames >= diff:
                            process_frame_counts[pid] += diff
                            available_frames -= diff
                            frame_action = "grew"
                        elif diff < 0 and current_frames > 1:
                            process_frame_counts[pid] += diff
                            available_frames -= diff
                            for _ in range(-diff):
                                if pamiec_procesow[pid]:
                                    strona = random.choice(list(pamiec_procesow[pid]))
                                    pamiec_procesow[pid].remove(strona)
                            frame_action = "shrunk"

                # Zbieranie logów
                log_data.append({
                    'timestamp': current_time,
                    'process_id': pid,
                    'current_wws_size': wws_size,
                    'allocated_frames': process_frame_counts[pid],
                    'process_suspended': suspended[pid],
                    'frame_action': frame_action
                })

            # Wznawianie procesów
            for pid in range(process_count):
                if suspended[pid]:
                    wws_size = wws_sizes[pid]
                    if wws_size <= available_frames and wws_size > 0:
                        suspended[pid] = False
                        process_frame_counts[pid] = wws_size
                        available_frames -= wws_size

                        # Przywracanie pamięci
                        pamiec_procesow[pid].clear()
                        unique_pages = []
                        seen = set()
                        okno = [p for p in recent_pages[pid] if p is not None]
                        for page in reversed(okno):
                            if page not in seen:
                                unique_pages.append(page)
                                seen.add(page)
                            if len(unique_pages) >= wws_size:
                                break
                        unique_pages.reverse()
                        pamiec_procesow[pid].update(unique_pages)

                        log_data.append({
                            'timestamp': current_time,
                            'process_id': pid,
                            'current_wws_size': wws_size,
                            'allocated_frames': process_frame_counts[pid],
                            'process_suspended': suspended[pid],
                            'frame_action': 'resumed'
                        })

            current_time += c

    return bledy_procesow, suspended, log_data
