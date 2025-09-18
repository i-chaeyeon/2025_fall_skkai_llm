## Problem(train_bpe): BPE Tokenizer Training (15 points)
import regex as re
from collections import Counter
from typing import List, Tuple, Dict
import os

def run_train_bpe_impl(input_path, vocab_size, special_tokens, **kwargs):

    ## Vocabulary Initialization
    vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}
    inv_vocab: dict[bytes, int] = {v: k for k, v in vocab.items()}

    ## Special tokens
    next_id = 256
    for s in special_tokens:
        b = s.encode("utf-8") 
        vocab[next_id] = b
        inv_vocab[b] = next_id
        next_id += 1

    ## Pre-tokenization
    PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
    counts = Counter()

    special_pattern = "|".join(re.escape(s) for s in special_tokens)
    
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = re.split(f"({special_pattern})", text)

    for chunk in chunks:

        if special_tokens and chunk in special_tokens:
            continue

        pre_tokens = [m.group(0) for m in re.finditer(PAT, chunk)]

        for pre_token in pre_tokens:
            b = pre_token.encode("utf-8")
            seq = tuple(bytes([x]) for x in b)
            counts[seq] += 1


    ## Compute BPE Merges
    merges: List[Tuple[bytes, bytes]] = []

    while len(vocab) < vocab_size:
        pair_counts = Counter()
        for seq, freq in counts.items():
            for a, b in zip(seq, seq[1:]):
                pair_counts[(a, b)] += freq

        if not pair_counts:
            break

        best_pair, freq = max(pair_counts.items(), key=lambda kv: (kv[1], kv[0]))
        a, b = best_pair

        new_token = a + b
        vocab[next_id] = new_token
        inv_vocab[new_token] = next_id
        merges.append((a, b))

        new_counts = Counter()
        for seq, c in counts.items():
            new_seq = []
            i = 0
            while i < len(seq):
                if i + 1 < len(seq) and seq[i] == a and seq[i + 1] == b:
                    new_seq.append(new_token)
                    i += 2
                else:
                    new_seq.append(seq[i])
                    i += 1
            new_counts[tuple(new_seq)] += c
        counts = new_counts

        next_id += 1

    return vocab, merges

# vocab, merges = run_train_bpe_impl(
#         "debug_input.txt",
#         267,
#         ["<|endoftext|>"]
#     )

# print(vocab)
# print(merges)