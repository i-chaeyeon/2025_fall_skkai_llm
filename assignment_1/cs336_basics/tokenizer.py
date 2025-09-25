import regex as re
import json
from typing import Iterable, Iterator

PAT = r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""

# {
#     0: b'\x00', 1: b'\x01', 2: b'\x02', 3: b'\x03', 4: b'\x04', 5: b'\x05', 6: b'\x06', 7: b'\x07', 
#     8: b'\x08', 9: b'\t', 10: b'\n', 11: b'\x0b', 12: b'\x0c', 13: b'\r', 14: b'\x0e', 15: b'\x0f', 
#     16: b'\x10', 17: b'\x11', 18: b'\x12', 19: b'\x13', 20: b'\x14', 21: b'\x15', 22: b'\x16', 23: b'\x17', 
#     24: b'\x18', 25: b'\x19', 26: b'\x1a', 27: b'\x1b', 28: b'\x1c', 29: b'\x1d', 30: b'\x1e', 31: b'\x1f', 
#     32: b' ', 33: b'!', 34: b'"', 35: b'#', 36: b'$', 37: b'%', 38: b'&', 39: b"'", 
# }
# [ ## 257부터 merges
#     (b's', b't'), (b'e', b'st'), (b'o', b'w'), (b'l', b'ow'), 
#     (b'w', b'est'), (b'n', b'e'), (b'ne', b'west'), (b' ', b'newest'), 
#     (b' ', b'low'), (b'w', b'i')
# ]

class Tokenizer:

    ## Initialize
    def __init__(self, vocab, merges, special_tokens=None):
        self.vocab = vocab # int -> byte (decoding)
        self.inv_vocab = {} # byte -> int (encoding)
        for k, v in vocab.items():
            self.inv_vocab[v] = k

        self.merges = {pair: i for i, pair in enumerate(merges)} ## merge 내 요소를 key, value로는 merge 순서

        if special_tokens:
            self.special_tokens = sorted(special_tokens, key=len, reverse=True) ## 큰거부터
        else:
            self.special_tokens = []
        self.inv_special_tokens = {token: self.inv_vocab.get(token.encode('utf-8')) for token in self.special_tokens}


        if self.special_tokens:
            special_pattern = "|".join(re.escape(s) for s in self.special_tokens)
            self.special_pattern = re.compile(f"({special_pattern})")
        else:
            self.special_pattern = None
            
        self.pat = re.compile(PAT)

    ## file로 저장된 vocab, merges 불러오기
    def from_files(cls, vocab_filepath, merges_filepath, special_tokens=None):
        with open(vocab_filepath, 'r', encoding='utf-8') as f:
            vocab_raw = json.load(f)
        vocab = {int(k): bytes(v) for k, v in vocab_raw.items()}
        
        with open(merges_filepath, 'r', encoding='utf-8') as f:
            merges_raw = json.load(f)
        merges = [tuple(map(bytes, pair)) for pair in merges_raw]
        
        return cls(vocab, merges, special_tokens) ## Initialize로 넘겨서 시작

    ## byte -> int (inv 사용)
    def encode(self, text: str) -> list[int]:
        token_ids = []
        
        if self.special_pattern:
            chunks = self.special_pattern.split(text)
        else:
            chunks = [text]


        for chunk in chunks:
            if chunk in self.special_tokens:
                token_ids.append(self.inv_special_tokens[chunk]) ## special token은 바로 예외처리
            else:
                pre_tokens = re.findall(self.pat, chunk)

                for pre_token in pre_tokens:
                    pre_token_bytes = pre_token.encode('utf-8')
                    subwords = [bytes([b]) for b in pre_token_bytes]

                    while True: 
                        cur_merge_priority = 987654321
                        cur_merge_idx = -1

                        for i in range(len(subwords) - 1):
                            pair = (subwords[i], subwords[i+1])
                            if pair in self.merges:
                                priority = self.merges[pair]
                                if priority < cur_merge_priority: ## 더 높은 우선순위 있으면 갱신
                                    cur_merge_priority = priority
                                    cur_merge_idx = i
                        
                        if cur_merge_idx == -1: ## 하나도 없음
                            break

                        merged_words = subwords[cur_merge_idx] + subwords[cur_merge_idx + 1]
                        subwords = subwords[:cur_merge_idx] + [merged_words] + subwords[cur_merge_idx + 2:]
                    
                    ids = [self.inv_vocab[word] for word in subwords]
                    token_ids.extend(ids)
                    
        return token_ids


    ## 사실 잘 이해가 안되서 도움을 좀 받음...
    ## 메모리 클때 쪼개서 encode 코드로 그때그때 lazy하게 보내는 방식
    def encode_iterable(self, iterable: Iterable[str]) -> Iterator[int]:
        for text_chunk in iterable:
            yield from self.encode(text_chunk)

    def decode(self, ids: list[int]) -> str:
        token_bytes = [self.vocab.get(id, b'') for id in ids]
        text_bytes = b"".join(token_bytes)
        return text_bytes.decode('utf-8', errors='replace') ## replace handler 사용 - 디코딩 오류나면 대체 문자로 처리해줌
