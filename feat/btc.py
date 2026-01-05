from dataclasses import dataclass
from typing import List, Tuple, Optional

DUST_THRESHOLD_SAT = 546  # conservative legacy-ish dust threshold

@dataclass(frozen=True)
class Utxo:
    txid: str          # hex
    vout: int
    value_sat: int
    script_pubkey_hex: str  # locking script of the UTXO

def estimate_vbytes_p2wpkh(num_inputs: int, num_outputs: int) -> int:
    """
    Rough estimate for native segwit P2WPKH.
    Real-world vbytes vary; production should compute precisely from actual tx.
    """
    overhead = 10
    in_vb = 68
    out_vb = 31
    return overhead + num_inputs * in_vb + num_outputs * out_vb

def select_coins_largest_first(utxos: List[Utxo], target_sat: int) -> Tuple[List[Utxo], int]:
    utxos_sorted = sorted(utxos, key=lambda u: u.value_sat, reverse=True)
    selected = []
    total = 0
    for u in utxos_sorted:
        selected.append(u)
        total += u.value_sat
        if total >= target_sat:
            break
    return selected, total

def plan_spend(
    utxos: List[Utxo],
    send_amount_sat: int,
    feerate_sat_per_vb: int,
) -> dict:
    """
    Returns a plan describing chosen inputs, outputs count, fee, change.
    You still need a signing/tx library to actually construct/sign raw tx bytes.
    """
    # Start assuming recipient + change outputs
    est_vb = estimate_vbytes_p2wpkh(num_inputs=1, num_outputs=2)
    est_fee = est_vb * feerate_sat_per_vb
    target = send_amount_sat + est_fee

    selected, total_in = select_coins_largest_first(utxos, target)

    # Re-estimate with actual input count
    est_vb = estimate_vbytes_p2wpkh(num_inputs=len(selected), num_outputs=2)
    fee = est_vb * feerate_sat_per_vb
    change = total_in - send_amount_sat - fee

    # Dust handling: if change is too small, drop change output and add to fee.
    if change < DUST_THRESHOLD_SAT:
        est_vb2 = estimate_vbytes_p2wpkh(num_inputs=len(selected), num_outputs=1)
        fee2 = est_vb2 * feerate_sat_per_vb
        change2 = total_in - send_amount_sat - fee2
        # If change2 is negative, you need more inputs: re-run selection with bigger target.
        return {
            "selected": selected,
            "total_in_sat": total_in,
            "outputs": 1,
            "fee_sat": fee2,
            "change_sat": 0,
            "ok": change2 >= 0,
        }

    return {
        "selected": selected,
        "total_in_sat": total_in,
        "outputs": 2,
        "fee_sat": fee,
        "change_sat": change,
        "ok": change >= 0,
    }