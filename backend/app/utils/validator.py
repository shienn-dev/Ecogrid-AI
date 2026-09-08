import math


def validate_numeric(value, name, min_value=0.0, max_value=None):
    """
    Memvalidasi apakah nilai adalah tipe numeric (int/float), positif, dan berada dalam rentang tertentu.
    Menolak NaN dan Infinity agar tidak bocor ke perhitungan.
    Menerapkan clean code dengan mengembalikan tuple (is_valid, error_message).
    """
    if value is None:
        return False, f"Parameter '{name}' wajib diisi."

    # Tolak boolean (bool adalah subclass int di Python)
    if isinstance(value, bool):
        return False, f"Parameter '{name}' harus berupa angka numerik."

    try:
        val = float(value)
    except (ValueError, TypeError):
        return False, f"Parameter '{name}' harus berupa angka numerik."

    # Tolak NaN / Infinity — bisa merusak perhitungan & JSON serialization
    if math.isnan(val) or math.isinf(val):
        return False, f"Nilai '{name}' harus angka terbatas (bukan NaN/Infinity)."

    if min_value is not None and val < min_value:
        return False, f"Nilai '{name}' tidak boleh kurang dari {min_value}."

    if max_value is not None and val > max_value:
        return False, f"Nilai '{name}' tidak boleh melebihi {max_value}."

    return True, val
