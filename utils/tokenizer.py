from pygments import lexers
from pygments.token import Token
import re

def tokenizer_with_padding(code, ext, max_length=4096, pad_token='[PAD]'):

    code = masking(code, ext)

    tokens = re.findall(r"\s+|\n|\S+", code)
    if len(tokens) < max_length:
        tokens += [pad_token] * (max_length - len(tokens))
    else:
        tokens = tokens[:max_length]

    return tokens



def tokens_transfomer(tokens: list[str], vocab: dict, unk_token='[UNK]'):
    return [
        vocab.get(token, vocab[unk_token]) for token in tokens
    ]





def masking(code, ext):

    lexer = get_lexer_by_extension(ext)
    result = ""
    
    for token_type, value in lexer.get_tokens(code):
        
        if token_type in Token.Name:
            # 언더바로 분할해서 각 부분 마스킹
            parts = value.split('_')
            masked_parts = []
            for part in parts:
                if part:  # 빈 문자열이 아닌 경우만
                    v_count = sum(c.islower() for c in part)
                    V_count = sum(c.isupper() for c in part)
                    U_count = sum(not c.isascii() and c.isalpha() for c in part)
                    
                    mask = f"v{v_count}"
                    if V_count > 0:
                        mask += f"V{V_count}"
                    if U_count > 0:
                        mask += f"U{U_count}"
                    masked_parts.append(mask)
            result += '_'.join(masked_parts)
            
        elif "Comment" in str(token_type):
            def replace_word(match):
                word = match.group(0)
                s_count = sum(c.islower() for c in word)
                S_count = sum(c.isupper() for c in word)
                U_count = sum(not c.isascii() and c.isalpha() for c in word)
                
                if s_count == 0 and S_count == 0 and U_count == 0:
                    return word
                
                mask = "d"
                if s_count > 0:
                    mask += f"s{s_count}"
                if S_count > 0:
                    mask += f"S{S_count}"
                if U_count > 0:
                    mask += f"U{U_count}"
                return mask
            
            converted = re.sub(r'[a-zA-Z\u0080-\uFFFF]+', replace_word, value)
            result += converted
            
        elif token_type in Token.Literal.String:
            # 문자열 마스킹
            if len(value) >= 2:
                content = value
                
                # 언더바로 분할해서 각 부분 마스킹
                def replace_with_underscore(text):
                    parts = text.split('_')
                    masked_parts = []
                    for part in parts:

                        if part:
                            def replace_word(match):
                                word = match.group(0)
                                s_count = sum(c.islower() for c in word)
                                S_count = sum(c.isupper() for c in word)
                                U_count = sum(not c.isascii() and c.isalpha() for c in word)
                                
                                if s_count == 0 and S_count == 0 and U_count == 0:
                                    return word

                                mask = ""
                                if s_count > 0:
                                    mask += f"s{s_count}"
                                if S_count > 0:
                                    mask += f"S{S_count}"
                                if U_count > 0:
                                    mask += f"U{U_count}"
                                return mask
                            
                            masked_part = re.sub(r'[a-zA-Z\u0080-\uFFFF]+', replace_word, part)
                            masked_parts.append(masked_part)
                        else:
                            masked_parts.append('')
                    return '_'.join(masked_parts)
                
                masked_content = replace_with_underscore(content)
                result += masked_content
            else:
                result += value
                
        else:
            result += value
    
    return result


def get_lexer_by_extension(ext):

    ext_to_lexer = {
        '.py': 'PythonLexer',
        '.ts': 'TypeScriptLexer', 
        '.js': 'JavascriptLexer',
        '.java': 'JavaLexer',
        '.cpp': 'CppLexer',
        '.c': 'CLexer',
        '.go': 'GoLexer'
    }
    
    lexer_name = ext_to_lexer.get(ext.lower(), 'TextLexer')
    return getattr(lexers, lexer_name)()
