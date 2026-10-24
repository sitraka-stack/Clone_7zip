import heapq
import pickle

# ------------- Fonctions Utilitaires -------------
def int_to_bin(n, bits):
    """Retourne une chaîne binaire de longueur `bits` pour l'entier n."""
    return format(n, '0{}b'.format(bits))

# ------------- Codage de Huffman (Standard) -------------
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(frequency):
    heap = [Node(ch, freq) for ch, freq in frequency.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]

def build_huffman_codes(root, code, codes):
    if root is None:
        return
    if root.char is not None:
        codes[root.char] = code
    else:
        build_huffman_codes(root.left, code + "0", codes)
        build_huffman_codes(root.right, code + "1", codes)

def huffman_compress(data):
    # data est une chaîne (chaque caractère représente un octet)
    freq = {}
    for ch in data:
        freq[ch] = freq.get(ch, 0) + 1
    root = build_huffman_tree(freq)
    codes = {}
    build_huffman_codes(root, "", codes)
    compressed = "".join(codes[ch] for ch in data)
    return compressed, codes

def huffman_decompress(bit_string, codes):
    inv_codes = {v: k for k, v in codes.items()}
    decoded = ""
    temp = ""
    for bit in bit_string:
        temp += bit
        if temp in inv_codes:
            decoded += inv_codes[temp]
            temp = ""
    return decoded

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

def bytes_to_bitstring(b, num_bits):
    # Convertit les octets en chaîne binaire avec des zéros non significatifs pour atteindre la longueur num_bits
    return bin(int.from_bytes(b, byteorder='big'))[2:].zfill(num_bits)

# ------------- Tokenisation LZ77 et Empaquetage de Bits -------------
def lz77_tokenize(data, window_size=255, min_match=3):
    """
    Tokenise les données en utilisant un algorithme LZ77 simple.
    Retourne une liste de tokens.
    Chaque token est un tuple :
      (is_match, offset, length, literal)
    - Pour un token littéral, is_match est False et literal est un caractère.
    - Pour un token de correspondance, is_match est True ; literal est None.
    """
    tokens = []
    i = 0
    n = len(data)
    while i < n:
        best_length = 0
        best_offset = 0
        # Recherche d'une correspondance dans la fenêtre (taille limitée à 255)
        start_index = max(0, i - window_size)
        for j in range(start_index, i):
            length = 0
            while i + length < n and data[j + length] == data[i + length]:
                length += 1
                # S'assurer de ne pas faire de correspondance en se chevauchant au-delà de la position actuelle
                if j + length >= i:
                    break
            if length > best_length:
                best_length = length
                best_offset = i - j
        # Si une correspondance d'au moins min_match caractères est trouvée, générer un token de correspondance.
        if best_length >= min_match:
            tokens.append((True, best_offset, best_length, None))
            i += best_length
        else:
            tokens.append((False, 0, 0, data[i]))
            i += 1
    return tokens

def pack_tokens(tokens):
    """
    Convertit les tokens en une chaîne binaire.
    Pour un token littéral : émet le drapeau '0' suivi des 8 bits du caractère.
    Pour un token de correspondance : émet le drapeau '1' suivi de 8 bits pour le décalage et 8 bits pour la longueur.
    """
    bit_str = ""
    for token in tokens:
        if not token[0]:
            # Token littéral : drapeau 0 + caractère littéral (8 bits)
            bit_str += "0" + int_to_bin(ord(token[3]), 8)
        else:
            # Token de correspondance : drapeau 1 + décalage sur 8 bits + longueur sur 8 bits
            bit_str += "1" + int_to_bin(token[1], 8) + int_to_bin(token[2], 8)
    return bit_str

def unpack_tokens(bit_str):
    """
    Convertit une chaîne binaire en une liste de tokens.
    """
    tokens = []
    i = 0
    while i < len(bit_str):
        flag = bit_str[i]
        i += 1
        if flag == "0":
            # Token littéral : les 8 bits suivants représentent le caractère
            char_bits = bit_str[i:i+8]
            i += 8
            tokens.append((False, 0, 0, chr(int(char_bits, 2))))
        else:
            # Token de correspondance : 8 bits pour le décalage, puis 8 bits pour la longueur
            offset = int(bit_str[i:i+8], 2)
            i += 8
            length = int(bit_str[i:i+8], 2)
            i += 8
            tokens.append((True, offset, length, None))
    return tokens

def lz77_decompress_tokens(tokens):
    """
    Reconstruit le texte d'origine à partir de la liste de tokens.
    """
    output = ""
    for token in tokens:
        if not token[0]:
            output += token[3]
        else:
            offset = token[1]
            length = token[2]
            start = len(output) - offset
            for j in range(length):
                output += output[start+j]
    return output

# ------------- Compression / Décompression Hybride -------------
def hybrid_compress(input_file, output_file):
    # Lecture du texte d'origine
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        data = f.read()
    # Tokenisation LZ77
    tokens = lz77_tokenize(data)
    # Empaquetage des tokens en chaîne binaire
    token_bits = pack_tokens(tokens)
    # Remplissage (padding) de la chaîne binaire pour qu'elle soit un multiple de 8 bits
    pad = (8 - (len(token_bits) % 8)) % 8
    token_bits_padded = token_bits + "0" * pad
    total_bits = len(token_bits)  # Nombre de bits valides d'origine
    # Conversion de la chaîne binaire remplie en octets
    packed_bytes = bitstring_to_bytes(token_bits_padded)
    # Conversion de ces octets en une chaîne où chaque octet est un caractère (pour le codage de Huffman)
    huffman_input = ''.join(chr(b) for b in packed_bytes)
    # Application du codage de Huffman sur la chaîne
    huff_bit_str, huff_codes = huffman_compress(huffman_input)
    huff_total_bits = len(huff_bit_str)
    huff_bytes = bitstring_to_bytes(huff_bit_str)
    # Stockage de toutes les métadonnées nécessaires à la décompression
    to_store = {
        'huff_codes': huff_codes,
        'huff_total_bits': huff_total_bits,
        'pad': pad,            # Remplissage dans la chaîne binaire des tokens
        'packed_token_bits_len': len(token_bits),  # Nombre de bits des tokens d'origine
        'compressed_data': huff_bytes
    }
    with open(output_file, 'wb') as f:
        pickle.dump(to_store, f)
    print("Compression terminée. Fichier compressé sauvegardé sous :", output_file)

def hybrid_decompress(input_file, output_file):
    with open(input_file, 'rb') as f:
        stored = pickle.load(f)
    huff_codes = stored['huff_codes']
    huff_total_bits = stored['huff_total_bits']
    pad = stored['pad']
    token_bits_len = stored['packed_token_bits_len']
    huff_bytes = stored['compressed_data']
    # Conversion des octets Huffman en chaîne binaire
    huff_bit_str = bytes_to_bitstring(huff_bytes, huff_total_bits)
    # Décompression par Huffman pour récupérer la chaîne binaire des tokens empaquetés (sous forme de chaîne de caractères)
    huffman_output = huffman_decompress(huff_bit_str, huff_codes)
    # Conversion de la chaîne récupérée en octets
    packed_bytes = bytes([ord(ch) for ch in huffman_output])
    # Conversion des octets en chaîne binaire (avec remplissage)
    token_bits_padded = bytes_to_bitstring(packed_bytes, len(packed_bytes)*8)
    # Suppression du remplissage pour récupérer la chaîne binaire originale des tokens
    token_bits = token_bits_padded[:token_bits_len]
    # Dépaquetage des tokens à partir de la chaîne binaire
    tokens = unpack_tokens(token_bits)
    # Décompression des tokens pour reconstruire le texte d'origine
    original_text = lz77_decompress_tokens(tokens)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(original_text)
    print("Décompression terminée. Fichier de sortie sauvegardé sous :", output_file)

# ------------- Programme Principal -------------
if __name__ == '__main__':
    mode = input("Entrez le mode (c pour compresser, d pour décompresser) : ").strip().lower()
    if mode == 'c':
        input_file = input("Entrez le chemin du fichier à compresser : ")
        output_file = input("Entrez le chemin pour la sortie compressée (ex: compressed.bin) : ")
        hybrid_compress(input_file, output_file)
    elif mode == 'd':
        input_file = input("Entrez le chemin du fichier compressé (ex: compressed.bin) : ")
        output_file = input("Entrez le chemin pour la sortie décompressée (ex: decompressed.txt) : ")
        hybrid_decompress(input_file, output_file)
    else:
        print("Mode sélectionné invalide.")