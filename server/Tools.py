def twosComplement(num_bytes, decNumber):
    if num_bytes == 2:
        return decNumber - (
            int("0xFFFF", 16) if decNumber > int("0xFFFF", 16) / 2 else 0
        )

    elif num_bytes == 4:
        return decNumber - (
            int("0xFFFFFFFF", 16) if decNumber > int("0xFFFFFFFF", 16) / 2 else 0
        )


def intToHex(num_bytes, decNumber):
    if num_bytes == 2:
        return int(hex(decNumber & 0xFFFF), 16)

    elif num_bytes == 4:
        return int(hex(decNumber & 0xFFFFFFFF), 16)
