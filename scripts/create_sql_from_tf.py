import sys
from tf.app import use
import sqlite3
from unicodedata import normalize

book_to_index = { "Genesis": 1, "Exodus": 2, "Leviticus": 3, "Numbers": 4, "Deuteronomy": 5, "Joshua": 6, "Judges": 7, "Ruth": 8, "1_Samuel": 9, "2_Samuel": 10, "1_Kings": 11, "2_Kings": 12, "1_Chronicles": 13, "2_Chronicles": 14, "Ezra": 15, "Nehemiah": 16, "Esther": 17, "Job": 18, "Psalms": 19, "Proverbs": 20, "Ecclesiastes": 21, "Song_of_songs": 22, "Isaiah": 23, "Jeremiah": 24, "Lamentations": 25, "Ezekiel": 26, "Daniel": 27, "Hosea": 28, "Joel": 29, "Amos": 30, "Obadiah": 31, "Jonah": 32, "Micah": 33, "Nahum": 34, "Habakkuk": 35, "Zephaniah": 36, "Haggai": 37, "Zechariah": 38, "Malachi": 39}
def passage_to_index(passage):
    if passage[0] not in book_to_index:
        print(passage)
        print(passage[0])
        raise IndexError('Try using the right kind of book names bro')
    return book_to_index[passage[0]] * 1000000 + int(passage[1]) * 1000 + int(passage[2])


sqlFile = sys.argv[1]
jsonFile = sys.argv[2]

conn = sqlite3.connect(sqlFile)
c = conn.cursor()

# OLD: Remove checkout=local if you haven't updated the data files in a while
# Remove ":latest" to fix the rate limit thing
A = use('bhsa', hoist=globals(), checkout='local')


# def nullifyNaAndEmptyAndUnknown(list_to_reduce):
#     templist = list_to_reduce
#     keys_to_remove = set()
#     for key, value in templist.items():
#         if value == "NA" or value == "" or value == "unknown":
#             keys_to_remove.add(key)
#     for key in keys_to_remove:
#         templist[key] = None
#     return templist

def normify(word):
    return normalize('NFC', word)

definite_qualities = {"det": "Y", "und": "N", "NA": None}
def maybe_is_definite(n):
    definiteness = F.det.v(L.u(n, otype='phrase_atom')[0])
    return definite_qualities[definiteness]

def convert_part_of_speech (part):
    if part == "subs":
        return "noun"
    elif part == "adjv":
        return "adj"
    return part

def convert_gender (gn):
    if gn == "m":
        return "masc"
    elif gn == "f":
        return "fem"
    elif gn == "NA":
        return None
    else:
        return gn

def convert_na_to_none (value):
    if value == "na":
        return None
    return value

feature_functions = {
    "wid": lambda n: int(n),
    "text": lambda n: normify(F.g_word_utf8.v(n)),
    "trailer": lambda n: normify(F.trailer_utf8.v(n)),
    "qere": lambda n: normify(F.qere_utf8.v(n)),
    "consonantal_root": lambda n: normify(F.lex_utf8.v(n)),
    # .replace('=', '').replace('/','').replace('[',''),
    "lexeme": lambda n: normify(F.voc_lex_utf8.v(L.u(n, otype='lex')[0])),
    "realized_lexeme": lambda n: normify(F.g_lex_utf8.v(n)),
    "gloss": lambda n: F.gloss.v(L.u(n, otype='lex')[0]),

    "part_of_speech": lambda n: convert_part_of_speech(F.sp.v(n)),
    "person": lambda n: F.ps.v(n)[1] if F.ps.v(n) in ["p1", "p2", "p3"] else None,
    "number": lambda n: F.nu.v(n),
    "gender": lambda n: convert_gender(F.gn.v(n)),
    "tense": lambda n: F.vt.v(n), # vt = verbal tense
    "stem": lambda n: convert_na_to_none(F.vs.v(n).lower()), # vs = verbal stem

    "state": lambda n: convert_na_to_none(F.st.v(n).lower()), # construct/absolute/emphatic

    "is_definite": lambda n: maybe_is_definite(n),

    #REMOVE: "g_uvf_utf8": lambda n: F.g_uvf_utf8.v(n),
    #REMOVE: "g_cons_utf8": lambda n: F.g_cons_utf8.v(n),
    
    "g_prs_utf8": lambda n: normify(F.g_prs_utf8.v(n)),
    "pron_suffix_number": lambda n: F.prs_nu.v(n),
    "pron_suffix_gender": lambda n: convert_gender(F.prs_gn.v(n)),
    "pron_suffix_person": lambda n: F.prs_ps.v(n)[1] if F.prs_ps.v(n) in ["p1", "p2", "p3"] else None,
    
    "has_pronominal_suffix": lambda n: "Y" if F.g_prs_utf8.v(n) != "" else None,
    "phrase_function": lambda n: F.function.v(L.u(n, otype='phrase')[0]),
    # TODO: "genre" from https://github.com/ETCBC/genre_synvar/
    # TODO: "sdbh": lambda n: F.sdbh.v(n),
    # TODO: "lxx_lexeme": lambda n: F.lxxlexeme.v(n),
    # TODO: "accent": lambda n: F.accent.v(n),
    # TODO: "accent_quality": lambda n: F.accent_quality.v(n),
    # TODO: "transliteration": <use the npm package from Charles Loder>
    # MAYBE: `rela` seems to be similar to `function` - might be worth adding
    # DON'T BOTHER: qere_trailer_utf8"
    "phrase_node_id": lambda n: int(L.u(n, otype="phrase")[0]),
    "clause_node_id": lambda n: int(L.u(n, otype="clause")[0]),
    "sentence_node_id": lambda n: int(L.u(n, otype="sentence")[0]),
    "rid": lambda n: int(passage_to_index(T.sectionFromNode(n))), # This is the old `rid`
}
def features(n):
    r = {}
    for feature in feature_functions.keys():
        try:
            value = feature_functions[feature](n)
            if value is not None and value != "NA" and value != "" and value != "unknown":
                r[feature] = value
        except:
            continue
    return r

# for k in TF.features.keys(): print(k)

def sql_type(key):
    return "INTEGER" if key.endswith("_node_id") or key == "rid" else "TEXT"

print("Preparing sql file")
drop_table_sql = """
DROP TABLE IF EXISTS word_features
"""
fields = list(feature_functions.keys())
fields.remove("wid")
field_sql = ",\n    ".join(f'{k} {sql_type(k)}' for k in fields)
create_table_sql = f"""
CREATE TABLE word_features (
    wid INTEGER PRIMARY KEY,
    {field_sql}
)
"""
c.execute(drop_table_sql)
c.execute(create_table_sql)

fields_values = ", ".join(fields)
def do_insert(values_string):
    insert_sql = f"""
    INSERT INTO word_features (wid, {fields_values}) VALUES
    {values_string}
    """
    c.execute(insert_sql)
    conn.commit()

def sqlify(w):
    if w is None:
        return "NULL"
    else:
        return '"' + str(w) + '"'

print("Writing word_features to json")
import json
with open(jsonFile, 'w') as outfile:
    json.dump(fields, outfile)

BATCH_SIZE = 50000
values = []
i = 0
print("Inserting values ...")
for n in F.otype.s('word'):
    w = features(n)
    wid = w["wid"]
    feature_list = ",".join(sqlify(w[k] if k in w else None) for k in fields)
    values.append(f"""
    ({wid}, {feature_list})
    """)
    i += 1
    if i % BATCH_SIZE == 0:
        do_insert(",".join(values))
        values = []
        print(" ... " + str(i))

if len(values) > 0:
    print(" ... " + str(i))
    do_insert(",".join(values))

# No more arbitrarily numbered verse_node_id... (we'll add a parallel_id later)
# c.execute("SELECT DISTINCT(rid) FROM words ORDER BY rid")
# rids = c.fetchall()
# rid_list = list(map(lambda args: {"value": args[0], "rid": args[1][0]}, enumerate(rids)))
# print(rid_list)
# c.executemany('UPDATE words SET verse_node_id=:value WHERE rid=:rid', rid_list)
# conn.commit()

conn.close()
print("Done!")

