# utils/adaptive.py
import time
import logging
import threading

log = logging.getLogger(__name__)

class AdaptiveController:
    """
    Kelas dasar untuk kontrol adaptif.  Ini adalah kerangka; Anda perlu
    mengimplementasikan logika adaptif yang sebenarnya.
    """
    def __init__(self, initial_params=None):
        self.params = initial_params if initial_params else {}
        self.running = False
        self.lock = threading.Lock()  # Lock untuk akses thread-safe

    def start(self):
        """Memulai thread pengontrol adaptif."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()

    def stop(self):
        """Menghentikan thread pengontrol adaptif."""
        with self.lock:
            self.running = False
        if hasattr(self, 'thread') and self.thread.is_alive(): # Cek dulu ada atau tidak.
          self.thread.join()


    def _run(self):
        """Metode utama untuk thread adaptif (implementasi di subclass)."""
        raise NotImplementedError("Subclasses must implement _run method")

    def get_params(self):
        """Mendapatkan parameter adaptif saat ini (thread-safe)."""
        with self.lock:
            return self.params.copy()  # Return a copy

    def update_params(self, new_params):
      """Update parameters (thread-safe)."""
      with self.lock:
        self.params.update(new_params)

class SimpleRateController(AdaptiveController):
    """Contoh sederhana: Mengontrol laju serangan."""
    def __init__(self, initial_rate, max_rate, increase_factor=1.1, decrease_factor=0.9):
        super().__init__(initial_params={"rate": initial_rate})
        self.max_rate = max_rate
        self.increase_factor = increase_factor
        self.decrease_factor = decrease_factor
        self.last_adjustment_time = time.time()

    def _run(self):
        while self.running:
            # Contoh: Tingkatkan laju jika tidak ada respons, kurangi jika ada error
            # (Ini SANGAT sederhana dan perlu diganti dengan logika yang lebih canggih)
            current_rate = self.get_params()['rate']

            # --- Placeholder untuk logika adaptif yang sebenarnya ---
            # Di sini, Anda akan memantau respons target (misalnya, latensi,
            # tingkat keberhasilan koneksi, pesan error) dan menyesuaikan
            # parameter berdasarkan respons tersebut.
            # Contoh (SANGAT sederhana):
            if self.should_increase_rate():  # Anda perlu mengimplementasikan ini
                new_rate = min(current_rate * self.increase_factor, self.max_rate)
                self.update_params({"rate": new_rate})
                log.info(f"Adaptive: Increasing rate to {new_rate:.2f}")
            elif self.should_decrease_rate():  # Anda perlu mengimplementasikan ini
                new_rate = max(current_rate * self.decrease_factor, 1) # Minimal 1
                self.update_params({"rate": new_rate})
                log.info(f"Adaptive: Decreasing rate to {new_rate:.2f}")
            # ---------------------------------------------------------

            time.sleep(2)  # Periksa setiap 2 detik (bisa di-tweak)


    def should_increase_rate(self):
        """
        Contoh (sangat sederhana) heuristic untuk meningkatkan rate.
        GANTIKAN dengan logika yang lebih canggih berdasarkan monitoring.
        """
        # Misalnya, tingkatkan jika sudah lama sejak penyesuaian terakhir
        return time.time() - self.last_adjustment_time > 10

    def should_decrease_rate(self):
        """
        Contoh (sangat sederhana) heuristic untuk menurunkan rate.
        GANTIKAN dengan logika yang lebih canggih berdasarkan monitoring.
        """
        # Misalnya, kurangi jika ada error (Anda perlu mendapatkan informasi ini)
        # return error_rate > 0.1  # Contoh: Jika tingkat error > 10%
        return False # Defaultnya jangan turunkan

# Contoh penggunaan (dalam main.py atau modul serangan):
# controller = SimpleRateController(initial_rate=100, max_rate=1000)
# controller.start()
# ... (dalam loop serangan) ...
# current_rate = controller.get_params()['rate']
# ... (kirim paket dengan laju current_rate) ...
# ...
# controller.stop()  # Saat serangan selesai