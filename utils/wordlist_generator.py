# utils/wordlist_generator.py
import itertools
import logging
import string  # Import String

log = logging.getLogger(__name__)

def generate_wordlist(target_info=None, basic=True, advanced=False, custom_words=None):
    """
    Menghasilkan wordlist.

    Args:
        target_info: String informasi tentang target (opsional).
        basic: Jika True, hasilkan wordlist dasar (angka, huruf kecil).
        advanced: Jika True, tambahkan karakter khusus dan kombinasi.
        custom_words: List of strings, kata-kata custom

    Returns:
        List of strings (the wordlist).
    """

    characters = ""
    if basic:
        characters += string.ascii_lowercase
        characters += string.digits
    if advanced:
        characters += string.ascii_uppercase
        characters += string.punctuation

    if not characters:
        log.warning("No character set selected for wordlist generation. Returning empty list.")
        return []

    wordlist = []

    # Basic wordlist (lengths 1-3)
    if basic:
        for length in range(1, 4):
            for word in itertools.product(characters, repeat=length):
                wordlist.append("".join(word))

    # Wordlist berdasarkan info target (jika ada)
    if target_info:
        parts = target_info.split()  # Pisahkan kata-kata
        for part in parts:
            wordlist.append(part)
            # Tambahkan variasi (huruf besar/kecil)
            wordlist.append(part.lower())
            wordlist.append(part.upper())
            wordlist.append(part.capitalize())

            if advanced:  # Tambahkan kombinasi
                for other_part in parts:
                    if part != other_part:
                        wordlist.append(part + other_part)
                        wordlist.append(part.capitalize() + other_part.capitalize())
                        wordlist.append(part + other_part.capitalize()) # e.g., nameCity
                        wordlist.append(part.capitalize() + other_part)


    # Tambahkan custom words (jika ada)
    if custom_words:
        for word in custom_words:
            wordlist.append(word)
            if advanced:
                wordlist.append(word.lower())
                wordlist.append(word.upper())
                wordlist.append(word.capitalize())


    # Advanced wordlist (lengths 4-6, kombinasi, jika diminta)
    if advanced:
        for length in range(4, 7):
            for word in itertools.product(characters, repeat=length):
                wordlist.append("".join(word))

        # Tambahkan kombinasi angka dan simbol di awal dan akhir kata
        for word in list(wordlist):  # Buat salinan karena kita akan memodifikasi list
            for num in string.digits:
                wordlist.append(num + word)
                wordlist.append(word + num)
            for symbol in string.punctuation:
                wordlist.append(symbol + word)
                wordlist.append(word + symbol)


    return list(set(wordlist))  # Hapus duplikat dan kembalikan sebagai list


# Contoh penggunaan (dan untuk pengujian):
if __name__ == "__main__":
    # Contoh 1: Basic + target info
    wordlist1 = generate_wordlist(target_info="John Doe 1990", basic=True)
    print(f"Wordlist 1 (basic + target info): {len(wordlist1)} words")

    # Contoh 2: Advanced + custom words
    wordlist2 = generate_wordlist(advanced=True, custom_words=["password", "admin", "123456"])
    print(f"Wordlist 2 (advanced + custom words): {len(wordlist2)} words")

    # Contoh 3: Basic + Advanced + target info + custom words
    wordlist3 = generate_wordlist(target_info="Acme Corp", basic=True, advanced=True, custom_words=["secret", "confidential"])
    print(f"Wordlist 3 (all options): {len(wordlist3)} words")

    #Simpan ke File (Contoh)
    with open("wordlist_example.txt", "w") as f:
        for word in wordlist3:
            f.write(word + "\n")
    print("Wordlist saved to wordlist_example.txt")